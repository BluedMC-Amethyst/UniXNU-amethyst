# Building a single xnu object by hand

Most kernel work here is one file. Rebuilding one object and relinking is fast;
running the whole tree is not. Doing it by hand is easy to get wrong in ways
that are invisible at compile time and only show up as a device that freezes
before it prints anything.

This note records the recipe that reproduces the shipped `pe_init.o`
byte-for-byte, and the two flags that, if missed, produce a kernel that boots
to a frozen green bar.

## Why hand-built objects are dangerous

An object can compile cleanly, link cleanly with zero undefined symbols, and
still be wrong, because `-arch` and `--target` are independent:

- `-arch arm64` picks the CPU.
- `--target=arm64-apple-ios17.0` picks the platform.

The pexpert `.CFLAGS` file contains `-arch arm64` and
`-miphoneos-version-min=17.0` but **not** `--target`. The build system adds the
triple through `KCC`. If you copy `.CFLAGS` by hand and stop there, clang falls
back to the host triple and quietly emits a **macOS** object. `-arch arm64`
still succeeds, because arm64 exists on both platforms.

That object then fails to link:

```text
ld: building for iOS, but linking in object file built for macOS,
    file '.../pe_init-exact.o' for architecture arm64
```

If your link command is lenient, or you never relink, the mistake is invisible
until the device hangs.

## The second trap: per-file defines

`pe_init.c` has behaviour selected by `XNU_DT_PANIC_REGION`, which is **not** in
`.CFLAGS`. The build injects it per object, from
`scripts/build-xnu-4k-baseline.sh`:

```sh
EXTRA_MAKE_ARGS+=("pe_init.o_CFLAGS_ADD=-DXNU_DT_PANIC_REGION=$DT_PANIC_REGION")
```

With `CONFIG_XNU_DT_PANIC_REGION=y` in the board config, this is `1`.

What it changes, in `check_for_panic_log()`:

| Value | Path taken | Where the panic region comes from |
| --- | --- | --- |
| undefined / `0` | `PLATFORM_PANIC_LOG_PADDR` | `0x3c0fc000`, a Raspberry Pi 3 address |
| `1` | device tree | `pram` node plus `/chosen/embedded-panic-log-size` |

Both paths exist in the same source, so a missing define compiles fine and
produces a kernel with the wrong panic-region logic. `__text` size changes
(0x1224 versus 0x1180), which is the one visible clue in the object.

## How to tell which path an object took

```sh
# device-tree path: six SecureDTLookupEntry/GetProperty calls in the prologue
llvm-objdump --disassemble --macho pe_init.o | grep -c SecureDTLookupEntry

# strings only present on the device-tree path
llvm-objdump --macho --section=__TEXT,__cstring pe_init.o | grep -E 'pram|embedded-panic-log-size'

# the Pi3 path calls ml_io_map_wcomb with the literal address before any DT lookup
llvm-objdump --disassemble --macho pe_init.o | grep ml_io_map_wcomb
```

Expect six `SecureDTLookupEntry` hits and both strings for the shipped build.

## The recipe that reproduces the shipped object

Work from the build directory so `.CFLAGS`, `meta_features.h` and
`config_dtrace.h` resolve as they did originally:

```sh
cd UniXNU/out/amethyst/<os>/amethyst/tree/build/xnu/ios-obj/\
DEVELOPMENT_ARM64_BCM2837/pexpert/DEVELOPMENT
```

Then, in Python, because several `-D` values contain spaces:

```python
import re, subprocess
from pathlib import Path

flags = Path('.CFLAGS').read_bytes().replace(b'\0', b' ').decode().strip()
raw = [a for a in re.split(r' (?=-[A-Za-z])', flags) if a]

args = []
for a in raw:
    if a.startswith('-arch '):
        args += ['-arch', a.split()[1]]
    elif a.startswith('-include '):
        args += ['-include', a.split()[1].strip()]
    else:
        args.append(a)

# the two things the build system adds and .CFLAGS does not contain
args = (['/opt/unixnu-linux/llvm/bin/clang-24', '--target=arm64-apple-ios17.0']
        + args[1:]
        + ['-DXNU_DT_PANIC_REGION=1'])

tree = '/home/bluekyeet/SmallProject/UniXNU/out/amethyst/ipados-17.7.11-21H461/amethyst/tree'
subprocess.run(args + ['-xc', tree + '/.cache/xnu-work/pexpert/arm/pe_init.c',
                       '-c', '-o', '/tmp/pe_init.o'], check=True)
```

Two details matter:

- Split on ` (?=-[A-Za-z])`, not on spaces. Several defines look like
  `-DCONFIG_NMBCLUSTERS=((1024 * 256) / MCLBYTES)` and simple whitespace
  splitting tears them apart.
- `.CFLAGS` may contain NUL bytes; strip them before decoding.

## Verifying the result

Byte-for-byte, against the shipped object:

```sh
cmp <(llvm-otool -s __TEXT __text ORIG.o | tail -n +3) \
    <(llvm-otool -s __TEXT __text NEW.o  | tail -n +3) && echo TEXT MATCH
cmp ORIG.o NEW.o && echo OBJECT IDENTICAL
```

A correct rebuild is byte-identical, not merely the same size. Anything less
means a flag is still missing.

## Verifying the link

The kernel link is not fully deterministic: 16 bytes at Mach-O offset `0x14a8`
(the UUID) change on every run. That is the only permitted difference. Compare
sizes and section contents, never raw bytes.

One non-obvious requirement: **link the object from its original path**.
Relinking the identical object from another directory changes the kernel by 96
bytes, because the object path reaches the debug and string tables. Copy the
new object over the original path, link, then restore.

```sh
cp NEW.o "$ORIG_PATH"
# link with the unmodified filelist and a fresh output name
cmp -l old.macho new.macho | awk '{print $1}' | head -20
# expect exactly offsets 5289..5304 (0x14a8..0x14b7), the UUID
```

## What this explains

The candidate whose nested-panic fix looked correct froze at the green bar
before XNU started. The source change was real but irrelevant: the object had
been rebuilt without `--target` and without `-DXNU_DT_PANIC_REGION=1`, so it
carried the Raspberry Pi panic-region path and a macOS triple. Rebuilding with
both flags reproduced the shipped object exactly, and the revert was confirmed
by relinking to the last known-good kernel.

Record the flags with every hand-built object. The compiler will not.
