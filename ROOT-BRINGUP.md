# Amethyst root bring-up evidence

## Hardware-confirmed checkpoints

- The probe10 image detects the split `unixnu` partition.
- Enabling `native-ufs-root=1` publishes OS and SystemOS and reaches APFS root
  mounting. The initial kernel stops at `bsd_init.c:1100`, root authentication.
- The isolated owner-root candidate uses signed policies for the exact root
  windows, authenticated NativeUfs reads and mounted-device/provider/UUID checks.
  It proceeds past root authentication and reaches executable loading.
- Adding the pinned original 21H461 Static/System trust-cache bundle and its
  ADT reservation permits launchd/dyld execution. The latest supplied photo
  reports `/usr/lib/libSystem.B.dylib` missing, with no dyld cache, and a failed
  SystemOS role lookup. This is not evidence of a completed userland boot.

Android userdata persistence and raw log/export remain disabled throughout.
The owner signing key is local and must not be committed or distributed.

## Packaging requirements established during testing

The payload is FAT32. When changing its size, rebuild the BootShim: both the
ARM64 image length and the embedded-payload size passed in x2 must match the
actual bytes. Updating only the Android header or ARM64 length is insufficient.
The initial enlarged candidates failed discovery with `no boot entry found`.
The corrected handoff candidate reaches XNU. Preserve the working firmware
body and ADT platform identity while qualifying one change at a time.

## Current candidate, not hardware-tested

`Mu-amethyst-owner-cache.img` enables the existing authenticated SystemOS mount
and cache startup path, binding the signed SystemOS UUID
`8846FE78-2910-4297-AF97-D59BB6F8FC16`. Data mounting remains disabled.
Only the kernel changes relative to the tested trust-cache candidate.

SHA-256: `b44071d252d355733cf23608108a4d0da685d9eb70e5536866f8780b43396639`.

Host compilation, isolated kernel linking, prelink and payload round-trip
checks passed. Kernel/configuration/ADT/trust-cache comparisons confirm the
packaging scope. These checks do not establish successful SystemOS mounting
or shared-cache loading on hardware. Test using `fastboot boot`, never by
flashing the boot image. No root-image reflash or repartitioning is required.

## Reproducibility limitation

## SystemOS mount result and cache-carrier candidate

Photo `_X8A0087.JPG` beside the owner-cache image confirms SystemOS APFS mount
completion. Cache mapping then fails with `not on process' root volume nor
preboot volume`, followed by the missing libSystem/no dyld cache termination.
Thus mounting SystemOS alone did not satisfy the shared-region carrier policy.

The next candidate enables the existing `XNU_OWNER_CACHE_CARRIER` development
instrument in vm_unix.c. It requires read-only APFS root/cache mounts, the exact
signed OS/SystemOS UUIDs and devices, and the expected cache parent directory.
It does not unconditionally accept an arbitrary cache mount.

`Mu-amethyst-owner-carrier.img` SHA-256:
`45b06bcb5f30dfda9f6ee6912e0a2427736ccdc9b5d0f924bb84f59fbe49d4bb`.
Compilation, link, prelink and packaging comparisons passed; hardware untested.
The config, ADT, trust caches, shim, firmware body and DTB remain unchanged.

## Cache-carrier result and owner boot-set metadata

Photo `_X8A0088.JPG` beside the carrier image shows launchd running boot tasks.
The explicit fatal error is now failure to obtain `boot-manifest-hash`, followed
by PID 1 termination. This establishes progress beyond shared-cache rejection,
not a completed userland boot.

The next isolated candidate enables the existing owner boot-manifest producer
and caller. Its SHA-384 boot-set identifier is derived from both authenticated
signed policy envelopes, domain-separated as `VerifiedRoot.OwnerBootSet.v1`.
It is labelled as owner metadata and refuses to overwrite an existing firmware
identity. The NativeUfs digest query checks the exact device, UUID and provider
and zeroes output on refusal. No arbitrary Apple manifest hash is substituted.

`Mu-amethyst-owner-manifest.img` SHA-256:
`42fa46ad4a0d062a4ebe0ff5063c66b755f1e33965c3518ccd9c72524379f8b1`.
Compilation, isolated link with no undefined symbols, prelink and packaging
checks passed. Config, ADT, trust caches and firmware remain unchanged.
Hardware execution of metadata publication is untested. Data stays disabled.

## Owner-manifest hardware result: Data boundary

Photo `_X8A0089.JPG` beside the owner-manifest image shows launchd progressing
through additional boot tasks, beyond the previous missing boot-manifest error.
The visible fatal sequence is now tzinit reporting inability to locate Data,
an attempted system-partition reset failing with a read-only filesystem, and
PID 17 termination. Earlier boot tasks also report read-only paths under
`/private/var`. Transcription is from the supplied photo, not a captured log.

This is consistent with the known absence of a writable iPadOS Data seed/mount.
It does not justify enabling raw persistence on Android userdata or making the
authenticated root writable. Next inspect the existing RAM-backed Data seed and
owner Data mount path; persistent allocation requires a separately reviewed
write plan. No further root-image flash or repartitioning is indicated.

### Data-seed prerequisite checked

The existing `prepare-owner-data-fixture.py` creates APFS with macOS hdiutil,
copies the exact OS private/var tree while preserving symlinks and modes, and
records the new volume UUID. The owner Data mount path binds that UUID to a
RAM-backed provider, mounts it at /private/var and checks that the resulting
mount is writable APFS on the expected device.

No compatible Data seed was found in SmallProject or the local amethyst-work,
amethyst-known-good and amethyst-kernel-building trees. This Linux environment
has no hdiutil or mkfs.apfs. A supplied populated APFS Data seed, or access to
a macOS host to generate it, is the current prerequisite. Do not enable the
Data mount switch without that input or substitute Android userdata.

### macOS Actions seed produced

Run 41166657395 succeeded. Downloaded artifact metadata identifies a 2 GiB
populated APFS seed, UUID `4777B134-0723-48C0-A32B-333007AB6166`.
Local SHA-256 verification matches
`d048bdcee1fba522cf832e28485674f50b5ce583ce4300b3d56b429c05c74ce8`.
Existing DarwinBoot zero-page packing preserves that logical hash and produces
247140928 encoded bytes, SHA-256
`4a5bb921f50fcae4d42b681004ba1453f896a5e04846de6f195e6d92a430ead0`.
This is close to the loader's 256 MiB packed-input ceiling; do not silently
truncate it or load the entire logical disk as a dense boot input.
RAM-backed Data integration remains pending; the seed is not hardware-tested.

### RAM Data candidate assembled (host only)

`Mu-amethyst-owner-data.img` enables the existing RAM Data mount with the exact
Actions seed UUID. It supplies the losslessly packed seed as scratch-data.img,
adds only the PackedRAMDisk ADT reservation and initrd configuration, and keeps
root/cache verification and original trust caches. Raw persistence stays off.
Payload FAT32 grows to 400 MiB; the reproduced BootShim is rebuilt with matching
x2 size handoff and ARM64 total length. Firmware body and hardware DTB are kept.

SHA-256: `b4bb44db38f0c56a91cab45bb2202e9ea760509c4560af7f75d2f2b79229578c`.
Boot image size is 303636480 bytes; bootloader download capacity is unverified.
Compilation, isolated link/prelink, exact FAT file round-trips and size-handoff
checks pass. No phone storage writes were made. Data mount and memory capacity
remain hardware-untested; RAM Data changes are lost on reboot.

### Clean seed / smaller Data candidate

The large Data candidate transferred and received Booting OKAY, but the user
observed no firmware checkpoint and the device remained/reappeared in fastboot.
The reported 768 MiB download limit exceeds the 303636480-byte image; the exact
early failure cause is unconfirmed.

Actions run 41169591242 excludes staged apps before APFS writes, avoiding
nonzero blocks left after copy-then-delete. Its verified 2 GiB seed packs to
1011840 bytes, versus 247140928 previously. Logical SHA-256 is
`0ce5f13c50c9723fbc6033590d41143a30b7218d22b63b595fbbf96597f64516`;
UUID is `A173DCC8-1F31-46ED-9F67-DB2A68FC25DE`.

`Mu-amethyst-owner-data-small.img` restores the known-working 160 MiB payload,
uses that exact UUID in the rebuilt kernel, and is 80248832 bytes compressed.
SHA-256: `37a1baaa281e924be30aff01d5f04f26de1cb1173520938935c523c570095287`.
Seed hash/packing, compilation, link/prelink, payload round-trips and final
embedded UUID checks passed. Hardware untested. The earlier data-clean folder
contains an invalid intermediate explicitly marked DO-NOT-BOOT; it is not this
candidate. No phone storage writes were made.

### Small RAM Data hardware result

Photo `_X8A0091.JPG` beside the data-small candidate confirms execution through
`Early boot complete. Continuing system boot.` The earlier tzinit termination
is no longer the stopping point. The small candidate boots where the large
candidate had no visible firmware checkpoint; this supports a size/placement
regression but does not identify the bootloader's exact constraint.

The photo reports crashes in bluetoothd, SpringBoard, contextstored, seserviced
and CommCenter, with `Too many corpses being created`. The terminal panic names
`watchdogd` exiting with namespace 22, subcode 0x55, description `none`.
Repeated trust-cache-query refusal messages are also visible, but the image
does not establish their causal relationship to those crashes. No individual
process exception backtrace or crash report is available from this photo.

Next obtain process exit/crash evidence or targeted RAM-only diagnostics before
changing AMFI, watchdog policy or hardware-driver selections. Do not suppress
the watchdog panic as a substitute for diagnosing the service failures.

The isolated candidate scripts and signed policy inputs currently live in the
maintainer workspace, not this repository. This record documents evidence,
not a complete reproducible implementation. Upstreaming the build integration,
policy-generation checks and device/provider authorisation changes remains
required; do not represent this candidate as a released or qualified build.
