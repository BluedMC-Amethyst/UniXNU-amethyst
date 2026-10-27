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
| Status | **Early bring-up — build pipeline available, hardware boot unverified** |

## Bring-up status

The port has a working build pipeline for the device-specific UEFI firmware and is progressing through kernel and payload preparation. An experimental boot image was generated and tested with fastboot boot, but UniXNU did not reach a confirmed runtime milestone. The device was subsequently restored to its previous Android installation.

No successful UniXNU boot has been verified on the target hardware.

| Stage | Component | Status | Objective |
|---|---|---|---|
| 1 | UEFI | 🟡 Build completed | Firmware image generated; verify execution on hardware and obtain serial or framebuffer output |
| 2 | UniXNU bootstrap | 🟡 Build pipeline prepared | Confirm bootstrap execution and collect diagnostics |
| 3 | Payload | 🟡 Image generated / prepared | Verify payload files, hashes and ADT sidecar at runtime |
| 4 | DarwinBoot | ⏳ Unverified | Capture DARWINBOOT: diagnostics and confirm validation succeeds |
| 5 | XNU kernel | 🟡 Build pipeline available | Confirm kernel entry, platform expert initialization and ADT root discovery |
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

## Optional build targets

### Build userdata

The userdata image may require approximately 16 GB of additional disk space.

```bash
./unixnu build userdata -D ../UniXNU-amethyst
```

## Current blockers

- **UEFI runtime:** The firmware builds, but successful execution on amethyst has not been demonstrated.
- **Boot image validation:** The experimental image was rejected by the device's boot path or failed to progress into a confirmed UniXNU runtime. The precise failure stage remains undetermined.
- **Bootstrap and DarwinBoot:** Runtime diagnostics are unavailable until the early boot path is confirmed.
- **XNU entry:** Kernel compilation does not yet establish that XNU executes on the target device.
- **Hardware support:** Storage, display, input, power management and other platform functionality remain unverified.

## Next milestone

Establish a reproducible early-boot path and capture diagnostic output before attempting to validate later stages. Keep build artifacts and runtime observations separate in status reports; do not mark a stage as working based on compilation alone.

## Contributing and debugging

When reporting bring-up progress, include the relevant build output or serial log and identify the stage at which execution stops.

A successful compilation is useful progress, but hardware initialization and runtime behavior must be verified independently.