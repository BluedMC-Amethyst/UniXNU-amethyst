// SPDX-License-Identifier: BSD-2-Clause-Patent
// Minimal driver for sheng's UFS diagnostic log (package/BootLog.c).
//
// BootLog.c is normally ticked once a second by sheng's board-page monitor in
// BootProgress.c. Amethyst deliberately does not build that file: it is Sheng's
// diagnostic *renderer* (font drawing, log ring, pexpert console takeover) and
// this kernel has no such console to drive. Only the writer is wanted here, so
// this file supplies the one call it needs.
//
// boot_log_tick() is idempotent: the first call starts the writer thread when
// sheng-log=1, later calls return immediately. It also arms sheng's guarded
// autoreset, which stays inert unless sheng-autoreset=<seconds> is passed.
#include <kern/thread.h>
#include <kern/clock.h>
#include <kern/sched_prim.h>
#include <pexpert/pexpert.h>
#include <IOKit/IOLib.h>

extern void boot_log_tick(unsigned now) __attribute__((weak_import));

static uint64_t gStartTicks;
static int gThreadStarted;

static void boot_log_monitor(void *arg, wait_result_t result)
{
	(void)arg;
	(void)result;
	thread_set_thread_name(current_thread(), "boot-log");
	for (;;) {
		uint64_t ns = 0;
		absolutetime_to_nanoseconds(mach_absolute_time() - gStartTicks, &ns);
		if (boot_log_tick) {
			boot_log_tick((unsigned)(ns / 1000000000ULL));
		}
		IOSleep(1000);
	}
}

// Started from bsd_init once the BSD layer can run a kernel thread. Does nothing
// unless the writer is linked, so the same kernel boots with it built out.
void amethyst_boot_log_start(void)
{
	if (!&boot_log_tick || gThreadStarted) {
		return;
	}
	gThreadStarted = 1;
	gStartTicks = mach_absolute_time();
	thread_t thread = THREAD_NULL;
	if (kernel_thread_start_priority(boot_log_monitor, NULL, BASEPRI_KERNEL, &thread) == KERN_SUCCESS) {
		thread_deallocate(thread);
	}
}
