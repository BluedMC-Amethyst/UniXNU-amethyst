# UFS diagnostic log for Amethyst

Amethyst has no usable serial console: its device tree carries no
`boot-console`, `uart0` or `uart1` node, and SM7635 reaches eUSB2 through the
PMIC rather than a DWC3 block, so there is no USB CDC-ACM path either. Every
boot result therefore had to be read off the screen and transcribed by hand,
which is slow and lossy -- and useless when the screen stops updating.

sheng's `package/BootLog.c` (boot argument `sheng-log=1`) solves this with no new
hardware. Every two seconds it stores the kernel message buffer, the board page
text and any caught panic into a window that `NativeUfs` exposes, so a full boot
log can be read back over ADB.

## Where the window lives

The last 8192 blocks (32 MiB) of whichever partition carries the root image. On
this device that is **`unixnu`**, not `userdata`, so Android's data partition is
never written. The window sits in `unixnu`'s ~122 GiB free tail, clear of the
8.74 GiB root image plus a 4 MiB guard. See `rootLogGeometry` in
`drivers/ShengUfs/RootLayout.h`; the log used to be disabled outright on a split
device because it shared geometry with the Data store, which is deliberately
refused there. Logging is read-only with respect to both filesystems, so it no
longer has to share that fate.

## Order of operations

The kernel must be **prelinked** before it is packed. A plain linker output has
empty `__PRELINK_TEXT` / `__PLK_*` segments, so the kernel launches with no
drivers and stalls before the console. That mistake cost three device boots;
`pack-log.py` asserts the size and segment guard so it cannot happen silently.

```
python3 scripts/log/build-log.py       # BootLog.c, BootLogStandins.c -> .o
python3 scripts/log/gen-standins.py    # weak stand-ins for the rest
python3 scripts/log/build-stubs.py     # compile the generated stand-ins
# link, then prelink with .scratch/ufs-audit/prelink-candidate.py
python3 scripts/log/pack-log.py        # RAM image with sheng-log=1
```

Once booted, read it back in LineageOS Recovery:

```
python3 scripts/log/pull-log.py --out /path/to/result
```

`pull-log.py` resolves `unixnu`'s start and size from the recovery shell, copies
the last 32 MiB to `/tmp` (RAM), pulls it, and decodes with sheng's own
`read-sheng-log.py`. It never writes to the phone. If the window has no header
magic it says so explicitly ("nothing was written, or the window is not the
log"), which is different from a decode error -- so a failed test still tells you
whether the writer started.

## Notes on the port

* `BootLog.c` here is sheng's file at `08cde20` with one correction: it declared
  `native_swipe_stats[16]` and printed `native_swipe_stats[16]`, one element past
  the end. The same line exists upstream, so it is a genuine defect. `TouchProbe.cpp`
  writes the "heavy" start timestamp to slot **8** (just before the Control Center
  strokes) and that slot is otherwise never displayed; the reader meant 8.
* `boot_log_tick()` is normally driven by `BootProgress.c`, which also carries the
  console *renderer* (font drawing, log ring, pexpert takeover). There is no
  console here to drive, so `BootLogMonitor.c` reproduces just the one call: a
  thread started from `bsd_init` after `bsd_autoconf()` ticks it once a second.
* `gen-standins.py` does not hand-copy declarations. It parses `BootLog.c`'s own
  `weak_import` declarations and emits a definition of the identical type, all
  weak so a real driver always wins, reading as zero/empty. Functions become weak
  no-ops returning 0/NULL so the writer's `if (&fn)` tests stay false, which is
  what "not available" means to it. asteroids' `BootLogStandins.c` covers the
  board it was generated for but leaves 94 symbols undefined here.
