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

### Service-exit diagnostic candidate

Existing check-watchdogd-branches.py demonstrates, with explicitly substituted
APIs, that the pinned original watchdogd traps when IOWatchdog is absent on a
physical machine. This is a lead, not proof of the photographed fault.

`Mu-amethyst-service-exits.img` adds only bounded SERVICE_EXIT logging for the
six photographed failing services in kern_exit.c. It records pid, wait status,
signal and exit-reason namespace/code before committing the exit reason.
It does not suppress watchdogs, disable AMFI or change service exit policy.
SHA-256: `6a914780d3d7cd22b399f1c7174d5307bc7ed001e5cc32b51889c9a069bec504`.
Compilation, link/prelink and payload comparisons passed; hardware untested.
The configuration, ADT, trust caches, RAM seed and firmware are unchanged.

### Service-exit hardware evidence

Photo `_X8A0093.JPG` beside the service-exits image records:

- watchdogd pid 52: rv=0x5, signal=5, namespace=2, code=0x5 (SIGTRAP).
- SpringBoard: rv=0x6, signal=6, namespace=8, code=0x1, repeatedly.
- bluetoothd, contextstored and seserviced: the same SIGABRT/namespace 8/code 1.
- Final panic still reports watchdogd exiting, namespace 22/subcode 0x55.

The immediate watchdog exit evidence is distinct from the later panic reason.
SIGTRAP is consistent with the missing-IOWatchdog branch in the existing host
analysis, but no hardware fault PC or assertion string has established that
branch. The other service SIGABRTs remain separately unexplained. Do not treat
trust-cache query warnings as proof of code-signing rejection. Next evidence
needed: watchdog trap PC/LR and service abort payloads or exception reports.

### Fault-evidence candidate (host only)

`Mu-amethyst-service-faults.img` adds USER_BRK pid/PC/LR/ESR logging before
unchanged breakpoint exception delivery, and bounded SERVICE_ABORT reason-string
copying for selected failed services before unchanged abort handling. Failed
user-memory copies are reported, not dereferenced directly. The existing exit
diagnostics remain. No exception, watchdog or signing policy is bypassed.
SHA-256: `d0589f312be47beac899c480e65884f43d768016dcd095d50facc51749894a0b`.
Compile/link/prelink and unchanged non-kernel payload checks passed. Original
compiler warnings remain in the saved logs; runtime execution is untested.

### Service-fault result and library-path candidate

Photos `_X8A0099.JPG` and `_X8A0102.JPG` show bounded abort strings from
SpringBoard, bluetoothd and contextstored: they cannot dlopen
`/usr/lib/libobjc-trampolines.dylib` (no such file, not in dyld cache).
The watchdog separately traps; its address still needs exact-binary matching.

Existing check-owner-cryptex-fallback-checkpoints.py records that the dyld
fallback environment did not resolve this same library failure. Existing
check-owner-union-checkpoints.py records native union-root composition exposing
the original library in offline testing, not Amethyst hardware qualification.

The owner-union candidate selects that existing read-only authenticated native
union mount and disables the previous separate cache-carrier exception. Data
stays RAM-backed; original signatures and signed volume policies are retained.
Watchdog handling is unchanged, so this is not a claim to fix both failures.
SHA-256: `73c478d5bf60130761db524fbb37a8ce7bcb4bb6a64241a3f9ea2da3a50075e4`.
Compile/link/prelink and payload comparisons pass; hardware untested.

### Native union hardware result

Photo `_X8A0103.JPG` beside owner-union shows no repeated missing-libobjc
abort strings in the captured screen. bluetoothd exits with rv=0, signal=0,
namespace=0, code=0. This is progress past the earlier shared library failure,
not proof of a fully functional Bluetooth stack.

SpringBoard repeatedly traps at PC=LR=0x1a37db2ec, ESR=0xf2000000;
its exit is signal 5, namespace 2, code 5, rather than the prior SIGABRT.
watchdogd pid 52 traps at PC=LR=0x1001dab0c, ESR=0xf2000001;
another watchdogd instance traps at 0x100affb0c with the same ESR.
The final panic still names watchdogd. The first watchdog PC's low offset
matches the known original BRK site only after a possible ASLR adjustment;
exact loaded-image base evidence is still needed before claiming a match.

Next symbolicate SpringBoard's shared-cache trap and qualify watchdog image
base/branch. Do not patch either BRK instruction or suppress exception handling.

### Original binary/cache symbolication inputs verified

Actions run 41173567856 succeeded; every downloaded artifact passed SHA-256.
The original watchdogd hash matches the existing branch-test pin:
`ded4c688e1c2add74acf3e7f9eea5fe2c2c569180ce81492221877944d913a01`.

Searching original executable cache mappings for BRK #0 sites congruent with
the photographed SpringBoard PC at possible 16 KiB-aligned slides up to the
cache maximum yields one candidate: unslid 0x19f3df2ec, inferred slide 0x43fc000,
dyld_shared_cache_arm64.09 offset 0x62af2ec. Original local symbols place it in
`-[FBSDisplayMonitor _initWithBookendObserver:transformer:]` +0x47c.
The adjacent original CFString assertion is `failed to find the main CADisplay`.
This is a unique instruction/symbol/string match under the stated slide search,
not direct observation of the hardware shared-region slide register/state.

The next functional boundary is main-display discovery through the actual
display service/provider chain. A framebuffer text console alone does not
establish that CADisplay discovery or UI rendering works. Watchdog remains a
separate service issue; no breakpoint instructions were modified.

### Display integration inspection

Amethyst defconfig disables both XNU_NATIVE_LEGACY_DISPLAY and
XNU_NATIVE_MOBILE_DISPLAY. The selected local legacy source requires
OriginalLegacyFramebufferABI.h, which is absent. The catalog-pinned
GopFramebuffer cf3b42979a9c44219e7bb149543e6fc3388b58ed tree also lacks that
header. Existing host checks reference generated headers/build reports and
offline traces that are not available as a ready-to-link local display archive.
The local source explicitly describes its legacy class as not yet a published
system display. Do not claim a boot-argument-only fix or import an unqualified
vtable ABI. Next reconstruct/qualify the exact original Legacy ABI and provider
publication path, or obtain the matching missing generator/build artifacts.

Static requalification against the actual kernel-union candidate passes: exact
original IOMobileGraphicsFamily executable SHA-256
`2e044ee68c1650397e1435234ca6459206262e4c7ed709cb7131c6f664f9bd9b`,
constructor-derived Legacy vptr, 358 nonnull method slots, and nine pure-virtual
slots 211/213/245/246/306/307/337/338/345. This establishes layout facts only.
Method signatures, object allocation/lifecycle and provider publication remain
unqualified. The header/generator search found no matching artifacts in local
trees or queried upstream paths; no runnable display candidate was produced.

The isolated candidate scripts and signed policy inputs currently live in the
maintainer workspace, not this repository. This record documents evidence,
not a complete reproducible implementation. Upstreaming the build integration,
policy-generation checks and device/provider authorisation changes remains
required; do not represent this candidate as a released or qualified build.
