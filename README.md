# UniXNU for Xiaomi Redmi Note 14 Pro+ 5G (`amethyst`)

Device port of [UniXNU](https://github.com/UniXNU/UniXNU) for the Xiaomi Redmi Note 14 Pro+ 5G.

| Property | Value |
|---|---|
| Device | Xiaomi Redmi Note 14 Pro+ 5G |
| Codename | `amethyst` |
| SoC | `SM7635` |
| Architecture | ARM64 |
| Device repository | [BluedMC-Amethyst/UniXNU-amethyst](https://github.com/BluedMC-Amethyst/UniXNU-amethyst) |
| UEFI repository | [BluedMC-Amethyst/uefi-amethyst](https://github.com/BluedMC-Amethyst/uefi-amethyst/tree/amethyst) |
| Status | **Early bring-up — XNU executes through MMU enable** |

## Bring-up status

The port boots from RAM with `fastboot boot`. UEFI mounts the embedded payload,
UniXNU parses its configuration, DarwinBoot validates the kernel and ADT, and
XNU reaches its post-MMU entry probe. The current hang is inside
`_arm_vm_init`, before `_vm_set_page_size` returns.

| Stage | Component | Status | Objective |
|---|---|---|---|
| 1 | UEFI | ✅ Working | Boots through RAM-only `fastboot boot` with stock Amethyst ClockDxe |
| 2 | UniXNU bootstrap | ✅ Working | Menu and input work on hardware |
| 3 | Payload | ✅ Working | Embedded FAT payload mounts and `unixnu.toml` is parsed |
| 4 | DarwinBoot | ✅ Working | Inputs validate and `ExitBootServices` completes |
| 5 | XNU kernel | 🟡 Early execution | Entry, pre-MMU and post-MMU probes pass; `_arm_vm_init` currently hangs |
| 6 | Storage and root filesystem | ⏳ Unverified | Verify storage initialization, device publication and root mounting |
| 7 | Userland | ⏳ Unverified | Verify launchd startup and a visible SpringBoard state |

**Status legend**

- ✅ Working — verified on the target device.
- 🟡 Build/preparation complete — artifacts or infrastructure exist, but runtime behavior is not confirmed.
- ⏳ Unverified — no successful runtime evidence yet.

> Successful compilation does not establish that the firmware can execute on the device or that the kernel can boot. Stage completion requires runtime evidence, preferably serial logs.

## Build instructions

### Prerequisites

- macOS with a compatible Xcode installation.
- Homebrew.
- Git with recursive submodule support.
- The Xcode version expected by the UniXNU build environment.

The commands below assume that both repositories are cloned into sibling directories and that all build commands are executed from the UniXNU core repository.

### 1. Clone the repositories

```bash
git clone --recurse-submodules \
  https://github.com/UniXNU/UniXNU.git

git clone --recurse-submodules \
  https://github.com/BluedMC-Amethyst/UniXNU-amethyst.git
```

### 2. Enter the UniXNU core repository

```bash
cd UniXNU
```

### 3. Prepare the bootstrap environment

```bash
chmod +x "../UniXNU-amethyst/scripts/ci-bootstrap-candidate.sh"

bash "../UniXNU-amethyst/scripts/ci-bootstrap-candidate.sh"
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
  https://github.com/BluedMC-Amethyst/uefi-amethyst.git \
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
  "https://raw.githubusercontent.com/BluedMC-Amethyst/uefi-amethyst/refs/heads/amethyst/Resources/DTBs/amethyst.dtb" \
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
payload support is upstream, use UniXNU commit `b29a1d4` from branch
`bluekyeet/unixnu-amethyst:amethyst-embedded-payload` together with UEFI branch
`BluedMC-Amethyst/uefi-amethyst:amethyst` at or after `daf306bf`.

## Optional build targets

### Build userdata

The userdata image may require approximately 16 GB of additional disk space.

```bash
./unixnu build userdata -D ../UniXNU-amethyst
```

## Current blockers

- **XNU VM initialization:** `_arm_vm_init` does not return; the next probe is
  inside its early Mach-O and boot-argument processing.
- **Hardware support:** Storage, display, input, power management and other platform functionality remain unverified.

## Next milestone

Localize and fix the `_arm_vm_init` hang, then restore panic rendering and
continue to platform-expert initialization.

## Contributing and debugging

When reporting bring-up progress, include the relevant build output or serial log and identify the stage at which execution stops.

A successful compilation is useful progress, but hardware initialization and runtime behavior must be verified independently.
