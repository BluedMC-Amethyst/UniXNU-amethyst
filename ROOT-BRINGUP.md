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

The isolated candidate scripts and signed policy inputs currently live in the
maintainer workspace, not this repository. This record documents evidence,
not a complete reproducible implementation. Upstreaming the build integration,
policy-generation checks and device/provider authorisation changes remains
required; do not represent this candidate as a released or qualified build.
