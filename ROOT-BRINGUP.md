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

### Legacy generator located in the Sheng board repository

The matching generator is owned by UniXNU/UniXNU-sheng, not UniXNU core:
`scripts/build-gop-legacy-display.py` at
`08cde20edc3254ed6f7df8d0f5384fb887786e8f`. It generates the opaque Legacy
header and checks compiled vtable slots against original family targets.
`package/LegacyDisplayProbe.cpp` supplies the publication/provider integration.

Its header-generation portion was replayed against the independently checked
358-slot audit, in scratch only. The local NativeLegacyDisplay.cpp then compiled
successfully against the actual ARM64 kernel recipe (warnings recorded).
It is not linked or hardware-qualified. The complete upstream generator also
builds Sheng-specific touch/GPU/power/audio/Wi-Fi integrations and must not be
run wholesale on SM7635. The minimal display-only dependency extraction and
original-method binding audit remain before a safe Amethyst test candidate.

The recovered generator's original-binding audit now passes against the local
compiled Legacy object and actual kernel-union image: complete 358-slot vtable,
exact owned overrides, all original-class imports, IOSurface getter instruction
checks, original refresh sender/property bodies and constructor/destructor
chains. Generated bindings remain isolated in scratch. This is static evidence,
not proof that lifecycle/publication runs on Amethyst. Upstream publication
code calls Sheng-specific peripheral probes; those must be excluded rather
than supplied as pretend-success stubs. No display boot image is ready yet.

Display-only publication code now compiles with foreign peripheral calls
omitted, alongside the GOP presenter and Legacy object. Original method bindings
assemble, late metaclass objects are produced, and bsd_init compiles with its
existing Legacy lifecycle hooks enabled. The isolated link fails (exit 1) on
boot_progress_cancel_scanout, boot_progress_prepare_scanout,
boot_progress_pulse_anchor and boot_progress_stage. These optional upstream
hooks are unresolved in this static kernel baseline. Resolve the console/
scanout ownership contract before enabling framebuffer transfer; no no-op
ownership stubs or hardware image were produced.

### Scanout ownership resolved; display kernel links

The four missing hooks are owned by UniXNU-sheng `package/BootProgress.c` at the
same revision. Importing that file wholesale would drag in Sheng's boot-progress
console renderer (font drawing, log ring, pexpert console takeover), which is
unrelated to display discovery and would give a second writer access to the
firmware framebuffer.

Instead only the ownership primitives were extracted to
`.scratch/ufs-audit/display-recovered/BootScanoutOwnership.c`: the
`prepare`/`cancel`/`pulse_anchor`/`stage` entry points, the atomic
`yield_requested`/`render_busy` handshake, and the truthful
`boot_progress_display_owned` flag. `pulse_anchor` returns 0 (no diagnostic
anchor is registered because this kernel has no renderer) and `prepare_scanout`
returns 0 instead of stealing a frame from a busy writer. The object imports
only `_absolutetime_to_nanoseconds` and `_mach_absolute_time`. Hooks are C linkage;
the recipe compiles this file as C++, so they are pinned in an `extern "C"` block.

The isolated link then succeeds (exit 0) with zero undefined symbols:
`NativeLegacyDisplay.late.o`, `NativeGOPPresenter.late.o`,
`AmethystDisplayProbe.o`, `original-bindings.o` and `BootScanoutOwnership.o`
against the unchanged baseline kernel
(`.scratch/ufs-audit/display-recovered/kernel-native.macho`). The Legacy class,
its metaclass entries and both lifecycle probes are present with no external
imports. This is a host-side link result only; nothing has been booted.

### Candidate prepared: `amethyst-owner-union-display`

`staging/amethyst-owner-union-display/Mu-amethyst-owner-union-display.img`,
73.3 MiB (76,902,400 bytes), sha256
`ce89993c8db59bf12c317f66308266044fa56a8cb418331e60090832f8bc131a`.
Repacked from the hardware-proven `amethyst-owner-union` image
(`73c478d5bf60…`) with the shim rebuilt for the new payload size. One variable
changed in the kernel (`Payloads/kernel.macho`); the ADT, trust cache and packed
2 GiB Data seed are byte-identical to the proven baseline.

The only other edit is the boot argument list, which adds
`offline-mobile-graphics-load=1 offline-legacy-register=1` to reach the
already-compiled lifecycle hooks. Payload staging is 4 files, `scratch-data.img`
included. Not yet booted; requires `sudo fastboot boot` and photo capture.

### Boot attempt 1 of that candidate FAILED (phone healthy, nothing written)

Booting `ce89993c…` stalled at the graphical/green early-boot area before the
text console appeared. Android still boots normally; no partition was touched.

Two defects, both mine:

1. **The candidate could not have answered the display question.** The Legacy
   probe only retains the object at `offline-legacy-phase` 2/3/4 and only reaches
   `probe()`/`attach()`/`start()` and publication at **phase 4**. No phase was
   supplied, so it defaulted to 1, returned early and released the object. The
   driver never executed. This should have been checked before imaging.
2. **`boot_progress_stage` became live code.** In the proven baseline it was
   unused, so the linker discarded it; `bsd_init()` calls it as its first
   statement, before `PE_create_console()`. The hook is now a pure parameter
   no-op with no print, allocation, lock or clock read, and the ordering
   hazard is documented in the file.

Diagnostics were added so a silent gate can never be mistaken for a hang again:
`NativeLegacyDisplay: probe phase=… init=… base=… WxH depth=… rowBytes=… rotate=…`,
`deferred to bsd_autoconf boundary`, and
`lifecycle probe=%u attach=%u start=%u dt=%u nub=%u/%u phase=%u`.
The probe source is now regenerated from the pristine upstream file with counted,
asserted patches instead of hand edits.

### Second boot FAILED identically; real contradiction found

`88a81bac…` (phase=4) stalled at the same green/graphical point. Two of my own
fixes were irrelevant, and the reason the probe could never have worked is a
boot-argument contradiction:

The baseline args contain `-textconsole`, so `PE_create_console()` takes the
`kPETextMode` branch. The Legacy probe's first validity gate requires
`PE_current_console(&video) == 0` with `v_depth == 32` and a live `v_baseAddr`,
i.e. a **graphics-mode** console. With `-textconsole` it silently returns at
stage 2 and the driver never starts regardless of `offline-legacy-phase`.
Dropping `-textconsole` would remove the only readable diagnostics, so this needs
a deliberate decision, not another blind image.

The pre-console stall is still unexplained and is a **separate** fault. A
single-variable bisect was built to settle it.

### Bisect A: flag only, no driver

`staging/amethyst-bisect-legacy-flag/Mu-amethyst-bisect-legacy-flag.img`,
76,873,728 bytes, sha256 `d2ff8f475e4bc4307094f1038793a88105e77bff7c4bb9ee09f3665f8d2a9add`.

`sched`/`bsd_init` recompiled with only `XNU_NATIVE_LEGACY_DISPLAY=1` (baseline is
`0`). No display, presenter, ownership or binding objects are linked; the two
entry points the macro references are inert empty functions in one object.
Verified: zero undefined symbols, no `__ZTV19NativeLegacyDisplay`,
`native_legacy_display_allocate`, `native_gop_presenter_create` or
`boot_progress_prepare_scanout`. Boot arguments are byte-identical to the proven
baseline, `-textconsole` included; no `offline-legacy-*` arguments.

Interpretation: boots to "Early boot complete" ⇒ the macro is innocent and the
driver objects are at fault. Stalls identically ⇒ the macro alone is at fault.
Not yet booted.

### ROOT CAUSE FOUND: the candidates were never prelinked

Bisect A stalled identically, which disproved the flag hypothesis and exposed the
real fault. Both failed candidates were packaged from the **plain linker output**
(~91.6 MB, 87.4 MB) instead of a **prelinked** kernel (124,518,400 bytes).
Segment comparison made it unambiguous: the candidates had
`__PRELINK_TEXT`, `__PRELINK_INFO`, `__PLK_TEXT_EXEC`, `__PRELINK_DATA` and
`__PLK_DATA_CONST` **empty (filesize 0)**, i.e. none of the 30 pinned kexts were
present. A kernel with no driver ecosystem stalls before `PE_create_console()`,
which is exactly the green-screen stop. The flag, the phase gate and the
`boot_progress_stage` hook were all irrelevant; those earlier "fixes" changed
nothing observable.

The recorded build line in `.scratch/ufs-audit/preflight-kernel-build.log` shows
the missing step: `emit_prelink.py --kernel <linked macho> --prelinked
<kernelcache> --slide=-0x1000000 --root …×31 --early-security-init …`.

`.scratch/ufs-audit/prelink-candidate.py` now wraps that recipe. It is validated
by reproducing the hardware-proven baseline **byte-for-byte** (124,518,400 bytes,
sha256 `b2a7c77b8587c347…`) from `kernel-native.macho` (`22392c97ea1e…`). Pack
scripts now refuse any kernel under 115 MiB or lacking `__PRELINK_TEXT`, so this
omission cannot recur silently.

Bisect A repackaged, prelinked: 80,248,832 bytes, sha256
`841a92d00847a4aabc13be6731881e1982d2a4f57fff647aec3a9929ecbcc069`.
Verified in-image kernel is 124,518,400 bytes with all 17 segments including
every prelink segment; boot args still byte-identical to the baseline. Untested.

### Bisect A result: booted to the baseline checkpoint

The prelinked flag-only kernel reached the baseline boot checkpoint. That clears
`XNU_NATIVE_LEGACY_DISPLAY` as a cause and confirms the empty-prelink segments
were the entire fault. The three earlier "fixes" were addressing non-problems.

### Correction: `-textconsole` does NOT block the probe

An earlier note in this file claimed the probe could never run under
`-textconsole` because it needs a graphics-mode console. That was wrong and is
retracted. `PE_state.video` is populated from the boot args in `PE_init_platform`
(long before `PE_create_console`), and `kPETextMode` only clears
`gc_graphics_boot`; it does not clear `vinfo` or `PE_state.video`. So
`PE_current_console()` still returns the real `v_baseAddr`, `v_width`,
`v_height`, `v_depth` and `v_rowBytes`, the probe's gate passes, and diagnostics
stay readable. No boot-argument trade-off is required.

### Display candidate, correctly prelinked

`staging/amethyst-owner-union-display/Mu-amethyst-owner-union-display.img`,
80,273,408 bytes, sha256
`eee3e9f0134ad5bcd8b4bbe6905c966f6fd18f19cb27e699dff1a1ee7bc1a5e5`.

Rebuilt from the proven baseline with one kernel variable. Verified in-image:
kernel 124,604,416 bytes with all 17 segments including every prelink segment;
the three diagnostics are present; ADT, trust cache and packed Data seed are
byte-identical to the baseline. Args add only
`offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4`,
and `offline-legacy-unit-scale` stays unset so no display policy is invented.
Untested.


The isolated candidate scripts and signed policy inputs currently live in the
maintainer workspace, not this repository. This record documents evidence,
not a complete reproducible implementation. Upstreaming the build integration,
policy-generation checks and device/provider authorisation changes remains
required; do not represent this candidate as a released or qualified build.

## A real boot log instead of photographs

Every result above had to be read off the screen by hand, because Amethyst has no
usable serial console: its device tree carries no `boot-console`/`uart0`/`uart1`
node, and SM7635 reaches eUSB2 through the PMIC rather than a DWC3 block, so
there is no CDC-ACM path either. sheng's `package/BootLog.c` (boot argument
`sheng-log=1`) solves this without any new hardware: it stores the kernel
message buffer into the `NativeUfs` log window every two seconds, and the window
can then be read back over ADB.

### The log window lives in `unixnu`

`NativeUfs` used to disable logging whenever the root image was in a split
partition, because the log window and the Data store shared one geometry and the
Data store is deliberately refused there. The log is read-only with respect to
both filesystems, so it now has its own geometry (`rootLogGeometry` in
`RootLayout.h`): the last 8192 blocks (32 MiB) of whichever partition carries the
root image. On this device that is `unixnu`, so **Android's `userdata` is never
written** -- the 32 MiB window sits in the ~122 GiB free tail of `unixnu`,
clear of the 8.74 GiB root image plus a 4 MiB guard.

### An out-of-bounds read in the upstream writer

`BootLog.c` declared `native_swipe_stats[16]` and then printed
`native_swipe_stats[16]`, one element past the end, in the `[swipe2]` row. The
same line exists in `UniXNU-sheng` at `08cde20`, so this is a genuine upstream
defect rather than a porting artefact. `TouchProbe.cpp` writes the "heavy" start
timestamp to slot **8** (immediately before the Control Center strokes) and that
slot is otherwise never displayed; the reader meant 8. Corrected to `[8]`.

### Linking a static kernel against the writer

`BootLog.c` reads every optional probe through `weak_import`, but a static kernel
link still needs a definition for each one. asteroids' `BootLogStandins.c` was
generated against a newer sheng build and leaves 94 symbols undefined on this
board (the adreno buffer/diag arrays, `native_legacy_*` probe arrays, cpufreq,
keyevents, mic, and the board-page renderer buffers). Rather than hand-writing
them, `gen-standins.py` parses `BootLog.c`'s own `weak_import` declarations and
emits a definition of the identical type -- weak, so a real driver always wins,
and reading as zero/empty so the log prints those rows blank. Functions get weak
no-ops returning zero rows. Correction: a defined weak function has a nonzero
address, so `if (&fn)` passes. String-returning stand-ins must satisfy the
caller's contract; see the tag fix below.

`bsd_init.c` now calls `amethyst_boot_log_start()` after `bsd_autoconf()`, which
starts a small thread that ticks `boot_log_tick()` once a second. sheng's own
ticker lives in `BootProgress.c`, which also carries the console *renderer*
(font drawing, log ring, pexpert takeover) that this kernel has no console for, so
only the one call is reproduced.

### Log candidate

`staging/amethyst-log/Mu-amethyst-log.img`, 80,285,696 bytes, sha256
`3a6d3531f2e6455dde520bb92fccf8c9c63b93ca4593381cc2e42c251aeb3f74`.

Rebuilt from the proven baseline with one kernel variable and one boot argument.
Verified in-image: kernel 124,764,160 bytes (baseline 124,518,400; the difference
is the log code) with every real prelink segment populated -- `__PRELINK_TEXT`
6,963,200 bytes, `__PLK_TEXT_EXEC` 20,447,232 bytes, `__PRELINK_INFO` 483,328,
`__PRELINK_DATA` 1,392,640, `__PLK_DATA_CONST` 3,555,328 -- and
`amethyst_boot_log_start`, `boot_log_tick`, `native_ufs_log_open` and
`native_ufs_log_write` all resolved. ADT, trust cache and the packed Data seed
are byte-identical to the baseline. Args add only `sheng-log=1`. Untested.

Read the result back with `pull-log.py`: it resolves `unixnu`'s start and size
from the recovery shell, copies the last 32 MiB to `/tmp` (RAM), pulls it, and
decodes with sheng's `read-sheng-log.py`. A window whose header magic is absent
means the writer never started, which is reported distinctly from a decode error.
Nothing is written to the phone.

### 2026-11-01: empty log and tag stand-in correction

The user booted the log candidate successfully through fastboot and reported
the same screen behavior as the baseline. Recovery extraction returned 32 MiB,
but the decoder reported eight zero magic bytes. This does not establish that
BSD initialization was never reached: the baseline reaches userspace service
failures and a watchdogd-related panic.

Static audit found `boot_progress_tag()` returning NULL in the generated
stand-ins. The writer calls `strlcpy(h.tag, boot_progress_tag(), ...)` before
writing its first header. Its function-address guard passes because the stub
is defined. The corrected stand-in returns an empty string. Disassembly
confirms the original returned zero and the replacement returns a string
address. This is a concrete defect, not yet a hardware-confirmed explanation.

Corrected candidate (old image preserved):
`staging/amethyst-log-tagfix/Mu-amethyst-log-tagfix.img`, 80,285,696 bytes,
SHA256 `d4efafc765738110c561b71625a482e1933107c04918029fd58f40afdcc7b748`.
Kernel SHA256 `4b0c6f9cc6de4947bd53e58258e0bc358d67709d2639d9e5fb27ee2d715f3546`;
124,764,160 bytes, 17 segments, required prelink segments populated, zero
undefined symbols in the linked kernel. `check-standins.py` passes.
BSD hook, storage driver, and boot arguments are unchanged from the log test.
Hardware test pending; no boot or partition operation performed by the agent.

### 2026-11-01: tagfix still empty; actual linked UFS object corrected

The user decoded the tagfix extraction: magic was still eight zero bytes.
Audit of `tagfix-link-command.json` found `NativeUfs-owner.o` was linked, not
`NativeUfs-logunix.o`. The earlier replacement targeted the wrong object name;
both log candidates therefore retained the original split-device log refusal.
Replacing the object naively exposed missing `_native_verified_block_manifest_sha384`
and `_boot_progress_poll`; no stubs were added for these. Instead, the saved
owner-enabled source was retained, with only the log geometry/open implementation
updated. Root-authorization behavior and the baseline no-poll path are preserved.

New candidate: `staging/amethyst-log-unixnu/Mu-amethyst-log-unixnu.img`,
80,285,696 bytes, SHA256
`c1cfb428bc062415f33f49a5ceb77109a57336b8cc759e384574ef89dcc4302c`.
Prelinked kernel SHA256
`ef3b826563dffa0adf36cbbe29337227643146812303ee214813fb9cc9bde691`.
Compile and link exited 0, linked kernel has zero undefined symbols, pack
checks passed. Scratch source and exact link command are in
`.scratch/ufs-audit/logkit/NativeUfs-owner-logunix.cpp` and
`unixnu-link-command.json`. Untested on hardware; old candidates preserved.
Saved-file decoder now imports Unix serial modules only in the serial path;
an import-blocking check confirms decoding can reach header validation without
`termios` or `tty`. Actual Windows validation remains with the user.

### Headerless trace run; direct startup candidate

The user observed the BSD-hook marker and monitor thread status 0 on the trace
candidate, but no later marker was noticed. Partition-relative recovery read
also decoded as eight zero magic bytes. Thread creation is confirmed, execution
of the monitor is not. XNU's kernel_thread_start_priority already calls
thread_start; there is no missing resume operation.

BootLog's tick is one-shot initialization which starts its own writer. Removed
the redundant monitor thread, naming and time conversion: the confirmed BSD
hook now calls boot_log_tick(0) directly. Writer/storage code unchanged from
the trace run. This is a targeted simplification, not a proven root cause.

`staging/amethyst-log-direct/Mu-amethyst-log-direct.img`, 80,285,696 bytes,
SHA256 `de63e64c53cf6db372f591f0dfaca386eff766c2f89190b38e5937460c80eca5`.
Kernel SHA256 `7775bf8194cd1d34dbef187bb128b73e7fec1f4e9b2a2c08128f5c0f3616963d`.
Compile/link exit 0, no undefined symbols, prelink/pack guards pass. No monitor
symbol remains in linked output. Hardware test pending.

Reader correction: dd on sda34 requires partition-relative skip 33546240, not
disk LBA 124206848. Earlier claims of a toybox seek limitation were incorrect.
The user tested the corrected read; it too was headerless. Decoder failures now
exit without a redundant Python traceback. Windows saved-file decoding reaches
the header check after moving Unix-only imports into serial initialization.

### Synchronous first snapshot, after direct-start also yielded no header

Direct-start extraction was headerless. No runtime failure point is established.
The first durable record previously depended on writer scheduling and completion
of the optional-probe formatter. BootLog now opens the same bounded log window
in the confirmed BSD hook and saves a message-buffer snapshot plus a version-4
header tagged `bsd-startup`, before starting the writer thread. The writer reuses
the already-open window rather than opening it again. Failed message writes
produce a header with zero message bytes and a write error; no slots are claimed.
Storage bounds, root authorization, and boot arguments are unchanged.

Candidate: `staging/amethyst-log-snapshot/Mu-amethyst-log-snapshot.img`.
SHA256 `256e30f4f63bdb91483954af5cfb9bcc81eb700789f75ce4f9d5b9e18fbc37d7`.
Kernel SHA256 `c85c9054e00ea3b936fc44b2ef651f91ab6390125770980e07c9a9fd78c98a7d`.
Compile/link exit 0, zero undefined symbols, prelink/pack checks pass.
`check-startup-snapshot.py` verifies a zero-slot startup record decodes its
message buffer. This removes an observability dependency; it does not prove
that storage writes succeed on hardware. Hardware validation pending.

### Confirmed packaged-argument blocker: trailing sheng-log=0

Snapshot extraction is 33,554,432 bytes, all zero. Inspecting the actual boot
image revealed `sheng-log=1` inserted before the baseline's trailing
`sheng-log=0`. XNU PE_parse_boot_argn_internal continues scanning numeric
arguments; the last matching value overwrites earlier values. Both tick and
UFS logMode therefore saw zero. Earlier claims that checking presence of
`sheng-log=1` proved logging enabled were wrong. This explains why even the
synchronous path produced no record, without requiring a scheduler theory.

Packer now replaces the existing disabled setting and asserts exactly one
`sheng-log=` occurrence. Reuses the snapshot kernel without recompilation.
`staging/amethyst-log-enabled/Mu-amethyst-log-enabled.img`, SHA256
`6c1c2cbb7e9f1ffae56817b2c3ecc15b732eb6472a50dcfb94aa6aa71f3c33ef`.
Verified by extracting unixnu.toml from the new image's FAT payload: exactly
one sheng-log=1, no sheng-log=0. Hardware test pending. No device operation
performed by the agent.

### Hardware success: enabled logging, boot ID 36da18c0

User booted amethyst-log-enabled and extracted a valid SHLOG001 v4 window:
46 rounds/slots, uptime 90 seconds, write_errors=0, msg_bytes=71967, state=2.
Absolute first LBA 124206848, window 8192 blocks. Evidence copied beside image
at `staging/amethyst-log-enabled/untagged-36da18c0/`; log.bin SHA256
`63e3fc3ff10ce9b921a1a401a98c6ef8fe22471c9bf036f45f4d77db3d5be4f8`.

Messages establish the actual sequence: BSD hook at 43.952956 s, parsed mode=1,
synchronous snapshot refused with `no root layout`, writer thread created with
status 0, writer entered at 46.914786 s, window opened at 47.931938 s,
first round write/sync=1. Thus async startup and naming do work; storage becomes
ready after the BSD hook, and the writer's retry handles that timing.

Recorded service failures include watchdogd pids 52/94 exiting with signal 5,
namespace=2/code=0x5, and repeated SpringBoard USER_BRK PC/LR 0x1a456b2ec.
These addresses are not yet symbolicated. gpt=1/1 is not a successful GPT
integrity check: the checker returns 1 when split-device Data-store geometry
is invalid. Zero write errors establishes logger-reported success, not that
separate integrity check. No new hardware boot is needed to inspect this log.

### Enabled-run trap analysis (offline)

`check-enabled-traps.py` in scratch passes against the hash-pinned original
watchdogd. PC 0x1008e2b0c has one original BRK #1 candidate under a 16-KiB-aligned
slide: 0x10000ab0c, slide 0x8d8000. Original instructions load string 0x10000ce37
before the trap: `connect_to_kext() unexpectedly failed - unable to lookup
watchdog KEXT service`. Second PC 0x100e71b0c maps uniquely to the same site
under 4-KiB alignment, slide 0xe67000; a 16-KiB-only assumption misses it.
These are candidate matches, not directly measured loaded-image bases.

SpringBoard PC 0x1a456b2ec is consistent with the previous original-cache
BRK #0 at unslid 0x19f3df2ec, inferred slide 0x518c000. Rechecked BRK bytes at
cache .09 offset 0x62af2ec. Previous local-symbol/string analysis identifies
`-[FBSDisplayMonitor _initWithBookendObserver:transformer:]` +0x47c and
`failed to find the main CADisplay`. No new slide measurement was obtained.

Thus main-display discovery and watchdog service lookup remain distinct
functional boundaries. No trap or service-exit policy was patched. Next display
experiment must combine the qualified display-only provider with the now-working
logger, preserve owner-enabled UFS authorization, and assert exactly one enabled
log argument. Do not boot the old display image expecting it to persist logs.

### Display provider plus proven logger candidate

Built `staging/amethyst-display-log/Mu-amethyst-display-log.img`,
80,310,272 bytes, SHA256
`dd13686267eb973e528b32911842d8833fa36184981ae513b86e49da0e7448f2`.
Kernel 124,850,176 bytes, SHA256
`69b90038257fb12de0a88b76af7e0ca203cccacea884f0e2dffc0b96ee8db55a`.
Uses the enabled-run logger and owner-authorized log-capable UFS object.
BSD source compiled with XNU_NATIVE_LEGACY_DISPLAY=1. Adds the previously
audited display-only provider, late Legacy/presenter objects, original bindings,
and scanout ownership primitives (not Sheng's renderer or peripheral probes).
Adds only offline-mobile-graphics-load=1, offline-legacy-register=1 and
offline-legacy-phase=4 to the logging baseline arguments; no invented unit scale.

358-slot compiled ABI audit passes; compile/link exit 0, zero undefined symbols.
Extracted-image check confirms exactly one enabled log setting, all three display
settings, 17 segments and nonempty required prelink segments. Watchdog handling
and storage bounds unchanged. Hardware untested; no agent device boot performed.
Exact scratch link command: `.scratch/ufs-audit/logkit/display-log-link-command.json`.

### Display-plus-log hardware result: stale log, not provider success

User confirmed fastboot sent and handed off Mu-amethyst-display-log.img
(78428 KB, both operations OKAY). Subsequent extraction still reports boot ID
36da18c0, 46 rounds and 71967 message bytes; saved result-display/log.bin was
byte-identical to the earlier enabled-run log (SHA256 63e3fc3f...d5be4f8).
No new persistent log is established. Fastboot handoff is not XNU boot success.

Source ordering explains the observability gap: native_mobile_graphics_load_probe
runs immediately after vfsinit; its enabled path loads IOMobileGraphicsFamily
and invokes native_legacy_display_probe. bsd_autoconf subsequently invokes
native_legacy_display_late_probe before returning. Only after bsd_autoconf
returns does amethyst_boot_log_start execute. Therefore either display phase
can prevent the logger from starting. This is an ordering fact, not evidence
identifying a particular failed call. Do not call this a successful display test
or erase the previous log to manufacture a new result. Next integration must
establish logging/root readiness before entering the experimental display path.

### Durable-log gate before display experiment

Moved the initial graphics load/probe from post-vfsinit and the late probe from
inside bsd_autoconf to after bsd_autoconf and logger startup. Display calls are
gated on a release/acquire flag set only after a successful header write and
sync (or a complete periodic round). Wait uses IOSleep(10), bounded to ten
seconds; on timeout display is skipped. Original display internals, watchdog
handling, root authorization and write bounds are unchanged. Gate readiness
establishes a log exists; it does not establish display success.

Candidate `staging/amethyst-display-durable/Mu-amethyst-display-durable.img`,
80,310,272 bytes, SHA256
`12827315e930f35fcf04c1542435bf6ccb2950e4b8787b0082a9201430c3fad4`.
Kernel SHA256 `53f635a14f0d9893193b54b331cd7ad5f42b206b3b74507bce999730aca12794`.
Compile/link exit 0, zero undefined symbols, prelink/pack guards pass.
`check-display-durable.py` verifies single display entry points follow the gate;
startup snapshot decode check passes. Scratch BSD source is the patched build
tree file; exact link command is logkit/display-durable-link-command.json.
Hardware test pending. Build integration remains workspace-dependent.

### Durable display run hardware result: gate passed, display path faulted

User extracted result-display-durable: new boot ID 279746e5 (664225509),
rounds=1, slots=1, write_errors=0, msg_bytes=19598. This is a genuinely new
record, so the durable gate worked: the logger started, wrote its header,
synced, and the writer opened the real window at LBA 124206848.

The message buffer ends at `AmethystBootLog: window first=124206848 blocks=8192`
with no `AmethystDisplay:` marker, no `NativeLegacyDisplay:` output, and no
recorded writer round 1 line. The display gate releases the boot thread as soon
as the durable flag is set, which happens inside the writer's first round just
before its round-1 IOLog and its 2000 ms IOSleep. The fault therefore occurred
inside the display load/probe before the writer's next message-buffer snapshot.
The trap reason is only on the photographed screen; image analysis was not
available to this session and the on-screen text was not transcribed.

Absence of `NativeUfs: ...` or `NativeLegacyDisplay:` markers is not evidence
that a specific call failed: the writer snapshots at 2 second intervals, so any
messages emitted after round 1 were lost when the machine trapped.

Candidate `staging/amethyst-display-flush/Mu-amethyst-display-flush.img`,
80,310,272 bytes, SHA256
`b65d963fadd4a41ac3ac48c8bcb03bcdbf09e56082df9dc99761e7d935dc2879`;
kernel SHA256 `1fe966f1a4bbc995c570010eb456943f90a72a645b78ad963be2849520e51df5`.
It adds `amethyst_boot_log_flush()`, a bounded synchronous checkpoint that
writes the message region and a state=5 header, then syncs under
IOLockTryLock so a busy writer causes a skip rather than a boot-thread stall.
Flush checkpoints bracket the experiment: gate-wait-done, before-graphics-load,
after-graphics-load, after-late-probe, plus gate-timeout. Display internals,
watchdog handling, root authorization and UFS bounds are unchanged.
Compile/link exit 0, zero undefined symbols, prelink and pack guards pass,
`check-display-flush.py` and `check-display-durable.py` pass. Hardware untested.

### Display-flush run user transcript: launchd reached, then kernel data abort

The user transcribed the screen during the display-flush boot (photo text, OCR
mangled). Decoded sequence: disk1 OwnerData mounts, `load_init_program` loads
`/usr/appleinternal/sbin/launchd.development` then `/sbin/launchd`, launchd
calls `shared_region_check_np`, kernel logs
`vm_shared_region_start_address() failed`, then `Kernel data abort.`

Important qualification: this same shared-region message is **not** fatal here.
The successful boot 36da18c0 logged it twice at 48.372560/48.386938 s and
launchd continued to complete many boot tasks. `check-shared-region-panic.py`
asserts this from the saved log. The message is the documented ENOMEM
"shared region is empty" branch: `sr_first_mapping == -1`, i.e. dyld probing
before it maps the cache. It is a normal probe on this board, not the fault.

Reaching launchd is itself progress: the durable-log gate let the machine get
past bsd_autoconf and into userspace, where the earlier durable run had stopped
at round 1.

The transcribed PC/register dump cannot be symbolicated: no address in it lies
inside any segment of the tested kernel (checked against all 17 segment ranges).
The `Kernel data abort.` panic has a real PC on screen, but transcription mangled
it beyond use. `check-shared-region-panic.py` records all of the above.

Therefore the remaining unknown is the actual aborting instruction. Panic text
goes to the in-memory panic log, which `compose()` already folds into writer
slots, but the writer's next snapshot is up to 2 s away and the machine is
stopped at the abort. Resolving it needs the panic string persisted from panic
context, not more on-screen reading.

### Panic-hook candidate: persist the panic text from panic context

`panic()` formats its message and calls `PE_panic_hook()` on the dying CPU with
interrupts off, before the halt. `PE_arm_debug_panic_hook` is a writable
function pointer in the DEVELOPMENT build (see pexpert/arm/hwtrace/hwtrace.c),
so BootLog.c chains it: it saves the previous pointer, installs
`boot_log_panic_record`, and calls the saved hook afterwards, so panic tracing
is unchanged.

The record reuses the existing message region (`msg_first` for `msg_blocks`),
which is why it is written at all: the writer only snapshots every 2000 ms and
the machine is already halted. Layout: a `SHLOGPN1` header (text_bytes,
in_panic_context, the write/sync results actually accepted), then the panic
text, then the live message buffer. A single atomic guard makes it run at most
once so a nested panic cannot rewrite it or recurse. It only uses the pooled UFS
transfers that are already deadline-bounded, so it needs no interrupts.

Decoder: `read-sheng-log.py` checks for `SHLOGPN1` in the message region first
and then writes `panic.txt`, `panic-header.txt` and the pre-panic `msgbuf.txt`,
printing whether the medium accepted the write. Without this, a panic record
would be misread as an ordinary message buffer.

Candidate `staging/amethyst-panic-hook/Mu-amethyst-panic-hook.img`,
80,310,272 bytes, SHA256
`d5c967c7de9cb4b180c4390a360a0902b10e71da784e7c120a5a2466edb0de0a`;
kernel SHA256 `3f0685d0022cc2609d64adff946fbb1f0453e04880027f8a1b81641e8387375b`.
Compile/link exit 0, zero undefined symbols, `check-standins.py`,
`check-startup-snapshot.py`, `check-display-flush.py` and
`check-panic-record.py` pass; prelink and pack guards pass. The hook pointer was
confirmed to live in the writable `__data` segment, not `__const`.

This exists because the display-flush transcript's real abort PC was destroyed
by transcription. The next run should report the exact panic text and the last
pre-panic messages as files, with no screen reading required. Hardware untested.

### Second screen transcript: identical userspace panic, registers unreadable

A second transcription (panicking address differs, OCR mangled) shows the same
sequence: CryptexSystem volume mounts, OwnerData mounts, launchd loads, two
`check_np` ENOMEM probes, then `panic(cpu 0 caller 0xfffffff000bfd56c):
Kernel data abort.`

The register dump is not usable. OCR doubled every character and interleaved
glyphs, so `pc`, `lr`, `far` and `esr` cannot be reconstructed with confidence;
no candidate value from either transcript falls inside any segment of the
tested kernel. This is recorded so the reconstruction is not mistaken for
evidence.

Consistent with the earlier finding, the two `check_np` failures also appear in
the successful boot (48.372560 and 48.386938 s) and cannot be the fault.

Because the panic-hook image's only difference from the display-flush image is
the UFS record, the screen output of the two builds is identical. A transcript
alone therefore cannot say which build ran; only the pulled log can.

### Root cause of the userspace data abort: freed display object

The panic-hook image's own transcript carried readable values this time:
`pc 0xfffffff00bfeebf8`, `far 0x1158`, `esr 0x96000005`. Note the transcribed pc
has one extra hex digit; dropping it gives a value inside `__TEXT_EXEC`, which is
how it was symbolicated. ESR 0x96000005 = data abort, translation fault; FAR
0x1158 is a NULL pointer plus 0x158. `llvm-nm` places the pc at
`native_legacy_properties_now + 0x48`, and the instruction there is
`ldr x8, [x8, #0x158]` where `x8` came from `[x20]` and `x20` from the
`native_legacy_object` global. So the object's vtable pointer was zero: it had
been freed.

Source confirms the mechanism. `native_legacy_object` is published for
diagnostics but holds no reference, and both probe exit paths call
`display->release()` (`AmethystDisplayProbe.cpp` lines 477 and 582), freeing the
object once its last reference drops. The writer's second round then calls
`compose()`, which calls `native_legacy_properties_now()`, which dereferenced the
stale pointer. The first round's header survives; the second round faults, which
is why the saved log stops at `window first=...` with `slots_written=1`.

Two further defects made this hard to see, both fixed here:

1. The writer published nothing. `native_ufs_log_open` fails at startup with
   "no root layout", so `startup_first`/`startup_blocks`/`startup_boot_id` stayed
   zero after the writer later opened the window in its own locals. Both the
   flush path and the panic hook therefore returned early and wrote nothing. The
   writer now publishes the window and boot id it actually got.
2. The flush and panic hook borrowed `boot_log_buffer`, which the writer thread
   owns and may be mid-round in. They now share a separate pre-allocated
   `boot_log_panic_buffer`; panic context never allocates.

Fixes: `native_legacy_properties_now` refuses a released object
(`if(!display || native_legacy_released)return 0;`); the writer publishes its
window; the panic/flush path has its own buffer. Note the guard had to be made in
`.scratch/ufs-audit/upstream-LegacyDisplayProbe.cpp`, because
`compile-display-provider.py` regenerates `AmethystDisplayProbe.cpp` from it and
silently discarded the first attempt.

Candidate `staging/amethyst-display-guard/Mu-amethyst-display-guard.img`,
80,310,272 bytes, SHA256
`efb9a31edbbe6c9faa1c5080f0d9bb2ed826ab90aa41162e8c040cead5ad237c`;
kernel SHA256 `ea2fc6489d401f0e3fcff6abbfb842f14f78c19551dfde79cb466932a1de5bbb`.
Disassembly of the linked kernel confirms the released-object branch before the
vtable load. Compile/link exit 0, zero undefined symbols, prelink and pack guards
pass, all eight checks pass. Watchdog handling, root authorization and UFS write
bounds unchanged. Hardware untested.

### The green-bar freeze was my object build, not the panic fix

The candidate carrying the nested-panic fix froze at the green iBoot bar before
XNU printed anything, and no log could be pulled. The fix itself was never at
fault. The object was rebuilt by hand with the wrong flags.

Two flags were missing, and neither produces a compile error:

| Missing flag | Effect | How it shows |
| --- | --- | --- |
| `--target=arm64-apple-ios17.0` | clang falls back to the host triple and emits a **macOS** arm64 object; `-arch arm64` still succeeds | `ld: building for iOS, but linking in object file built for macOS` |
| `-DXNU_DT_PANIC_REGION=1` | the kernel takes the `PLATFORM_PANIC_LOG_PADDR` path (`0x3c0fc000`, a Raspberry Pi 3 address) instead of the device tree | `__text` is 0x1224 instead of 0x1180; no `pram` string; `ml_io_map_wcomb` called before any `SecureDTLookupEntry` |

`.CFLAGS` in the pexpert build directory contains `-arch arm64` and
`-miphoneos-version-min=17.0` but **not** `--target`, and never contains
`XNU_DT_PANIC_REGION`. The build adds the triple through `KCC` and the define
per object through
`pe_init.o_CFLAGS_ADD=-DXNU_DT_PANIC_REGION=$DT_PANIC_REGION`
(scripts/build-xnu-4k-baseline.sh). Both have to be supplied by hand.

With both flags present, the rebuilt `pe_init.o` is **byte-identical** to the
shipped object (136,416 bytes, `cmp` clean, all sections matching), and
relinking reproduces `kernel-guard.macho` exactly apart from the 16-byte UUID at
offset `0x14a8`. The full recipe and the traps are in
[OBJECT-BUILD.md](OBJECT-BUILD.md).

One further trap found while verifying: the object must be linked **from its
original path**. Linking the identical object from another directory shifts the
kernel by 96 bytes, because the path reaches the debug and string tables.

### Nested-panic cascade: the board provides no usable panic region

Separate from the freeze above, and still valid. The display-guard transcript
shows `round=1 write/sync=1` (the flush fix is live), then `Nested panic
detected`, a mutex-unexpectedly-owned abort at lock_mtx.c:175, `Nested panic
count: 3`, `pe_init.c:707 Assertion failed: panic_info`, count 4, count exceeds
limit 5, then `Nested panic stall. Stage 2 bailout`.

`check_for_panic_log()` (pexpert/arm/pe_init.c) obtains the panic region from the
device tree's `pram` node plus `/chosen/embedded-panic-log-size`. The Amethyst
device tree has neither, checked with `dtc` against
`.scratch/ufs-audit/owner-baseline.dtb`. The alternative path is
`PLATFORM_PANIC_LOG_PADDR 0x3c0fc000` from pexpert/pexpert/arm64/BCM2837.h,
which is a Raspberry Pi 3 DRAM window and meaningless on this SoC. Either way
`gPanicBase` and `panic_info` stay 0 for the whole boot.

`PE_update_panicheader_nestedpanic()` asserts on that NULL, and it is only
reachable when a second panic occurs. The first fault therefore becomes
assert -> panic -> nested -> mutex abort -> reset, and the original panic text is
destroyed before anything can persist it. That is why two runs in a row lost the
real fault even though the logger was writing.

The proposed fix makes that function return without asserting when `panic_info`
is NULL. Nesting is still reported by the caller
(`check_and_handle_nested_panic` prints the nested panic string and count), so
only header maintenance with no storage to update is skipped. Nothing suppresses
the original panic.

**Status: not shipped.** It is correct in itself, but it cannot be evaluated on
hardware until a rebuild with the correct flags reaches XNU. The image that
froze did not contain the fix as intended, so the earlier attempt proved nothing
about it either way.

The original fault is still unidentified. Its `panic_caller` values
(0xfffffff000bf4434, 0xfffffff000bf1168) do not resolve to any instruction in the
tested kernel after correcting for transcription digit doubling, so they were not
used to name a function.

### Recovery image

`pe_init.c` is restored to the revision the shipped object was built from, with
the nested-panic fix removed, so line 707 holds `assert(panic_info)` again.

The kernel was relinked from the unmodified filelist and reproduces
`kernel-guard.macho` exactly apart from the 16-byte UUID at `0x14a8`: identical
size (92,008,368 bytes), zero undefined symbols, and all five prelink segments
byte-identical in size to the last known-good image
(`__PRELINK_TEXT` 6,963,200, `__PRELINK_INFO` 483,328, `__PLK_TEXT_EXEC`
20,447,232, `__PRELINK_DATA` 1,392,640, `__PLK_DATA_CONST` 3,555,328).

| Field | Value |
| --- | --- |
| Image | `staging/amethyst-recovery/Mu-amethyst-recovery.img` |
| Size | 80,310,272 bytes |
| SHA256 | `2292549bbfd826ef3c4f850619bf1eb73636b31e301cd900f62b3f2dd7b769c9` |
| Prelinked kernel SHA256 | `5e5982aa117f6d97c813d1e7810d6c4219f9dba10fd8fdfebd1785cbc4d5a5dc` |

Boot arguments and payloads are unchanged from `amethyst-display-guard`, the
last image that reached launchd, including the single `sheng-log=1` and the
display probe flags. Hardware untested.

`check-object-build.py` rebuilds `pe_init.c` with the recorded recipe and fails
unless the result is byte-identical to the shipped object, so a missing flag
cannot pass unnoticed again. All ten checks pass.
