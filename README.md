# UniXNU for Xiaomi Redmi Note 14 Pro+ 5G (`amethyst`)

Device port of [UniXNU](https://github.com/UniXNU/UniXNU) for the Xiaomi Redmi Note 14 Pro+ 5G.

| Property | Value |
|---|---|
| Device | Xiaomi Redmi Note 14 Pro+ 5G |
| Codename | `amethyst` |
| SoC | `SM7635` |
| Architecture | ARM64 |
| Device repository | [IOS4Amethyst/UniXNU-amethyst](https://github.com/IOS4Amethyst/UniXNU-amethyst) |
| UEFI repository | [IOS4Amethyst/uefi-amethyst](https://github.com/IOS4Amethyst/uefi-amethyst/tree/amethyst) |
| Status | **Kernel bring-up — text console works; root device is the current boundary** |

## Bring-up status

### Split-device storage safety

`unixnu` is preferred for root reads, with `userdata` fallback only when no
`unixnu` entry exists. On split devices, persistent Data and log/export opens
are disabled: Android userdata is F2FS, not a safe raw-write region. The
Partitioner's `reserve_mib` currently leaves an unallocated tail above unixnu;
it does **not** reserve blocks inside Android userdata. Do not run Apply based
on the earlier claim that this gap protects sheng persistence. A dedicated,
validated persistence allocation and reviewed device-write plan are still needed.
Host parser and store/log refusal tests pass; hardware writes are untested.
Board defaults explicitly set `sheng-data-persist=0`, `sheng-log=0`, and
`payload.adt.persistent_data=false`; the driver guard is defense in depth.

Host build evidence (2026-10-30): `./unixnu build kernel -D ../UniXNU-amethyst
-j 8` completed, including ShengUfs `71eeacb` and prelink. Output relative to
UniXNU: `out/amethyst/ipados-17.7.11-21H461/amethyst/kernel/kernel.macho`, SHA-256
`4cbec82154b2a9f229ea265246055a07dc4bd46e7cc42e8b5ff979215818c25a`.
The unchanged Static/System trust-cache modules fetched with `./unixnu ipsw
fetch` produced `out/ipsw/21H461/original-static-system.bundle`, SHA-256
`7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`, matching
the OS profile allow-list. Payload preflight stops on the missing platform seed
(`--unique-chip-id`); a compatible Data seed is also still absent. No new boot
image or hardware validation is claimed.

The port boots from RAM with `fastboot boot`. UEFI mounts the embedded payload,
UniXNU parses its configuration, DarwinBoot validates the kernel and ADT, and
XNU starts its scheduler, enters IOKit and reaches root mounting. The physical
GOP text console is visible on hardware. A guarded ApplePMGR provider satisfies
AMFI without advertising unimplemented power operations. The current panic is
`Failed to mount root device`; a compatible root image is not part of the
RAM-only test.

| Stage | Component | Status | Objective |
|---|---|---|---|
| 1 | UEFI | ✅ Working | Boots through RAM-only `fastboot boot` with stock Amethyst ClockDxe |
| 2 | UniXNU bootstrap | ✅ Working | Menu and input work on hardware |
| 3 | Payload | ✅ Working | Embedded FAT payload mounts and `unixnu.toml` is parsed |
| 4 | DarwinBoot | ✅ Working | Inputs validate and `ExitBootServices` completes |
| 5 | XNU kernel | ✅ Working | VM, scheduler, first context switch, IOKit, text console and AMFI/PMGR path pass |
| 6 | Storage and root filesystem | 🟡 Mount boundary reached | XNU attempts root mounting; provide and validate the configured userdata root |
| 7 | Userland | ⏳ Unverified | Verify launchd startup and a visible SpringBoard state |

**Status legend**

- ✅ Working — verified on the target device.
- 🟡 Build/preparation complete — artifacts or infrastructure exist, but runtime behavior is not confirmed.
- ⏳ Unverified — no successful runtime evidence yet.

> Successful compilation does not establish that the firmware can execute on the device or that the kernel can boot. Stage completion requires runtime evidence, preferably serial logs.

## Build instructions

### Prerequisites

- Linux with the UniXNU open-source Mach-O toolchain, or macOS with Xcode.
- Git with recursive submodule support.
- Python 3.11+, mtools and dtc.

On Linux, install the toolchain once from the UniXNU checkout:

```bash
sudo scripts/linux/setup-toolchain.py -j "$(nproc)"
scripts/linux/setup-toolchain.py --check
```

The commands below assume that both repositories are cloned into sibling directories and that all build commands are executed from the UniXNU core repository.

### 1. Clone the repositories

```bash
git clone --recurse-submodules --branch amethyst-embedded-payload \
  https://github.com/IOS4Amethyst/UniXNU.git

git clone --recurse-submodules \
  https://github.com/IOS4Amethyst/UniXNU-amethyst.git
```

### 2. Enter the UniXNU core repository

```bash
cd UniXNU
```

### 3. Prepare the bootstrap environment

```bash
chmod +x "../UniXNU-amethyst/scripts/ci-bootstrap-candidate.sh"

DEVICE_DIR=../UniXNU-amethyst bash "../UniXNU-amethyst/scripts/ci-bootstrap-candidate.sh"
```

### 4. Configure the device

```bash
./unixnu defconfig amethyst_defconfig -D ../UniXNU-amethyst
```

### 5. Build the XNU kernel

```bash
./unixnu build kernel -D ../UniXNU-amethyst
```

### 6. Clone the UEFI repository

```bash
git clone --recurse-submodules \
  --branch amethyst \
  https://github.com/IOS4Amethyst/uefi-amethyst.git \
  ../uefi-amethyst
```

If the repository already exists, update it instead:

```bash
git -C ../uefi-amethyst pull --recurse-submodules
git -C ../uefi-amethyst submodule update --init --recursive
```

### 7. Build the payload

```bash
./unixnu build payload \
  --unique-chip-id 0x1234567890abcdef \
  --uefi ../uefi-amethyst \
  --edk2 ../uefi-amethyst/Mu_Basecore \
  -D ../UniXNU-amethyst
```

Replace the example chip identifier with the appropriate value for your setup when required.

### 8. Build the firmware

```bash
./unixnu build firmware \
  --uefi ../uefi-amethyst \
  -D ../UniXNU-amethyst
```

### 9. Download the device tree blob (DTB)

```bash
curl -fL \
  "https://raw.githubusercontent.com/IOS4Amethyst/uefi-amethyst/refs/heads/amethyst/Resources/DTBs/amethyst.dtb" \
  -o "../UniXNU-amethyst/live.dtb"
```

### 10. Build the boot image

```bash
./unixnu bootimg \
  --uefi ../uefi-amethyst \
  --dtb ../UniXNU-amethyst/live.dtb \
  -D ../UniXNU-amethyst
```

The boot-image stage requires a valid DTB and a compatible UEFI implementation.

Amethyst's Android header-v4 bootloader exposes the installed vendor ramdisk
instead of the generic ramdisk supplied to `fastboot boot`. Until the embedded
payload support is upstream, use UniXNU branch
`IOS4Amethyst/UniXNU:amethyst-embedded-payload` at or after `20437c1` together
with UEFI branch `IOS4Amethyst/uefi-amethyst:amethyst` at or after `4e6782ba`.

## Optional build targets

### Build userdata

The userdata image may require approximately 16 GB of additional disk space.

```bash
./unixnu build userdata -D ../UniXNU-amethyst
```

## Current blockers

- **Root filesystem:** the RAM-only image reaches `Failed to mount root device`.
  Build and validate the configured userdata root before testing launchd.
- **Power management:** the ApplePMGR bridge only publishes the provider AMFI
  requires. Unimplemented power operations deliberately panic rather than touch
  unqualified registers.
- **Hardware support:** full display presentation, input, suspend, GPU and other
  board services remain unverified.

## Next milestone

Provide the root filesystem, verify UFS publication and mount the configured OS
volume. Keep root/userdata work separate from RAM-only kernel bring-up.

## Contributing and debugging

When reporting bring-up progress, include the relevant build output or serial log and identify the stage at which execution stops.

A successful compilation is useful progress, but hardware initialization and runtime behavior must be verified independently.
