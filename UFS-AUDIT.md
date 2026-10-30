# Amethyst UFS qualification — incomplete

Reference: https://unixnu.com/porting/ufs

## Source-backed hardware facts

MiCode/kernel_devicetree commit
`4a44b8da9f6a9b9e66c61e640d090b421f9d71be` (Volcano SoC source, not a live
Amethyst handoff measurement):

- `qcom/volcano.dtsi:1884–1889`: UFS host `0x01d84000`, size `0x3000`;
  additional ICE/HWKM windows are separate from the host.
- `qcom/volcano.dtsi:1890`: GIC SPI 265.
- `qcom/volcano.dtsi:1910–1918`: GCC/RPMh clocks and lane clocks.
- `qcom/volcano.dtsi:1998`: apps-SMMU stream `0x60`, mask `0`.
- `qcom/msm-arm-smmu-volcano.dtsi:73–78`: SMMU base `0x15000000`, size
  `0x100000`, QSMMU v500; driver maps only its bounded `0xd0000` subset.

These confirm several inherited constants, not firmware-state adoption safety.
GCC offsets, PHY/reset sequence, current SMMU context ownership, DMA reachability,
link/queue state and command completion still require qualification.

## Safety policy

Default `native-ufs-root=0`, no probe argument: NativeUfs's start gate returns
before controller access. This is intentionally not a working-root configuration.
Explicit `native-ufs-root=1` is needed only after reviewing the takeover path.
Data persistence and logging stay off. No cold-init writes are being guessed.

Local takeover change preflights SMMU compatibility before stopping the firmware
queue. This avoids queue writes on a known planning refusal, but does not prove
exclusive ownership or provide rollback after a later failure.

## Evidence levels

- Host SMMU planning/configuration tests: PASS.
- Host split store/log refusal tests: PASS, zero write-window opens.
- Amethyst host register access, DMA, known-block read, root mount: unverified.
- Production preflight-slice ASan/UBSan test: PASS; mapping/conflict refusals
  occur before queue access, and queue-stop failure propagates.
- Full kernel compilation and prelink with the preflight change: PASS,
  `./unixnu build kernel -D ../UniXNU-amethyst -j 8`, output relative to UniXNU:
  `out/amethyst/ipados-17.7.11-21H461/amethyst/kernel/kernel.macho`, SHA-256
  `278e24abd33312e66f14706c2386ae1cb80f0f902e1b28eef0edf879329e824a`.
  Hardware validation and rollback after queue stop remain pending.
- Kernel87 console/root-mount panic does not establish successful UFS access;
  its payload did not enable UFS root mode.
- New candidates' retained framebuffer does not isolate UFS as the stall cause.

No new hardware candidate should be published as a porting success on this basis.

## Queue failure quarantine follow-up

Queue-stop timeout, descriptor-address readback failure and queue-start timeout
now poison the transport and clear readiness; subsequent stop/start calls refuse
before MMIO. `tests/RootQueueFailure.cpp` exercises production `RootQueue.h`
under ASan/UBSan: busy firmware is untouched, all three failures quarantine,
and retry writes nothing. PASS. This does not restore firmware queue/SMMU state.

Full kernel build and prelink: PASS with the same command above; updated kernel
SHA-256 `14ac7f50dec39bb834883c32d94f088e15bbfafbc87145dfd72df4cead34ec8e`.
Hardware status is unchanged: takeover disabled by default, stall cause unknown,
no new phone image or device test performed.
