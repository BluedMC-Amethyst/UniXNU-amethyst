# UniXNU for Xiaomi Redmi Note 14 Pro+ 5G (amethyst)

UniXNU device support for the Xiaomi Redmi Note 14 Pro+ 5G (codename: `amethyst`, SoC: `SM7635`)

**Target OS:** iPhone X (`iPhone10,3`) userland, iOS 16.5 (20F66).

**Status:** Bring-up / Waiting for UEFI.

## Bring-up progress:
- [ ] **Stage 1: UEFI**
  - *Waiting for the SILICIUM port for amethyst.*
  - Goal: Firmware reaches the UniXNU application, framebuffer/serial shows output.
- [ ] **Stage 2: UniXNU**
  - *Blocked by Stage 1.*
  - Goal: Menu appears, configuration is parsed, driver/patch counts are logged.
- [ ] **Stage 3: Payload**
  - *Partially prepared (`board.toml`, `unixnu.toml` configs).* 
  - Goal: UniXNU reads payload files, hashes match, ADT sidecar is next to the kernel.
- [ ] **Stage 4: DarwinBoot**
  - *Blocked by Stage 1.*
  - Goal: Validates kernel, ADT, and trust cache, prints `DARWINBOOT:` to serial.
- [ ] **Stage 5: Kernel entry**
  - *CI Pipeline (macOS build) is set up to compile XNU.*
  - Goal: XNU starts, reaches platform expert, ADT root matches.
- [ ] **Stage 6: Storage and root**
  - *Blocked by Stage 4 & 5.*
  - Goal: Block driver publishes `userdata`, XNU mounts root (UUID match required).
- [ ] **Stage 7: Userland**
  - *Blocked by Stage 6.*
  - Goal: `launchd` runs, SpringBoard (UI) reaches a visible state.
