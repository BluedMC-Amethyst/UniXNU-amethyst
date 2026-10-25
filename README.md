# UniXNU for Xiaomi Redmi Note 14 Pro+ 5G (`amethyst`)

Device port of [UniXNU](https://github.com/UniXNU/UniXNU) for the Xiaomi Redmi Note 14 Pro+ 5G.

| Property | Value |
|---|---|
| Device | Xiaomi Redmi Note 14 Pro+ 5G |
| Codename | `amethyst` |
| SoC | `SM7635` |
| Architecture | ARM64 |
| Device repository | [andr0d1v/UniXNU-amethyst](https://github.com/andr0d1v/UniXNU-amethyst) |
| UEFI repository | [BluedMC-Amethyst/uefi-amethyst](https://github.com/BluedMC-Amethyst/uefi-amethyst/tree/amethyst) |
| Status | **Bring-up / Awaiting UEFI support** |

## Bring-up status

The port is currently in the early bring-up stage. The build environment and kernel compilation pipeline are available, while hardware boot and subsequent stages depend on a working UEFI implementation for `amethyst`.

| Stage | Component | Status | Objective |
|---|---|---|---|
| 1 | UEFI | ⏳ Blocked | Boot the UniXNU application and obtain framebuffer or serial output |
| 2 | UniXNU bootstrap | ⏳ Blocked | Initialize the bootstrap environment, parse configuration and report driver/patch counts |
| 3 | Payload | 🟡 Prepared | Load payload files, validate hashes and locate the ADT sidecar |
| 4 | DarwinBoot | ⏳ Blocked | Validate the kernel, ADT and trust cache; emit `DARWINBOOT:` diagnostics |
| 5 | XNU kernel | 🟡 Build pipeline ready | Enter the XNU kernel, reach the platform expert and validate the ADT root |
| 6 | Storage and root filesystem | ⏳ Blocked | Initialize storage, publish the userdata device and mount the expected root filesystem |
| 7 | Userland | ⏳ Blocked | Start `launchd` and reach a visible SpringBoard state |

**Status legend**

- ✅ Working — verified on the target device.
- 🟡 Prepared — configuration or build infrastructure exists, but runtime functionality is not yet verified.
- ⏳ Blocked / pending — depends on earlier stages or missing hardware support.

> Successful compilation does not imply successful boot on the target device. Stage completion should be based on runtime evidence, preferably serial logs.

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
  https://github.com/andr0d1v/UniXNU-amethyst.git
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

### 6. Build the payload

```bash
./unixnu build payload \
  --unique-chip-id 0x1234567890abcdef \
  -D ../UniXNU-amethyst
```

Replace the example chip identifier with the appropriate value for your setup when required.

### 7. Download the device tree blob (DTB)

```bash
curl -fL \
  "https://raw.githubusercontent.com/BluedMC-Amethyst/uefi-amethyst/refs/heads/amethyst/Resources/DTBs/amethyst.dtb" \
  -o "../UniXNU-amethyst/live.dtb"
```

### 8. Clone the UEFI repository

```bash
git clone --recurse-submodules \
  --branch amethyst \
  https://github.com/BluedMC-Amethyst/uefi-amethyst.git \
  ../UniXNU-amethyst/uefi-amethyst
```

If the repository already exists, update it instead:

```bash
git -C ../UniXNU-amethyst/uefi-amethyst pull --recurse-submodules
git -C ../UniXNU-amethyst/uefi-amethyst submodule update --init --recursive
```

### 9. Build the firmware

```bash
./unixnu build firmware \
  --uefi ../UniXNU-amethyst/uefi-amethyst \
  -D ../UniXNU-amethyst
```

### 10. Build the boot image

```bash
./unixnu bootimg \
  --uefi ../UniXNU-amethyst/uefi-amethyst \
  --dtb ../UniXNU-amethyst/live.dtb \
  -D ../UniXNU-amethyst
```

The boot-image stage requires a valid DTB and a compatible UEFI implementation.

## Optional build targets

### Build userdata

The userdata image may require approximately 16 GB of additional disk space.

```bash
./unixnu build userdata -D ../UniXNU-amethyst
```

## Current blockers

- UEFI support for `amethyst` is not yet available in the required state; the port is awaiting the relevant SILICIUM implementation.
- Runtime validation of the UniXNU bootstrap and DarwinBoot is pending a successful UEFI boot.
- Kernel entry, storage initialization, root filesystem mounting and userland startup remain unverified.

## Contributing and debugging

When reporting bring-up progress, include the relevant build output or serial log and identify the stage at which execution stops.

A successful compilation is useful progress, but hardware initialization and runtime behavior must be verified independently.

The immediate milestone is to obtain a working UEFI boot path for `amethyst`, allowing the remaining stages to be tested incrementally.
