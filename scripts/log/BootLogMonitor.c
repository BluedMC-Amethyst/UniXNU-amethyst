// SPDX-License-Identifier: BSD-2-Clause-Patent
// boot_log_tick() initializes once and starts its own writer thread.
// No renderer, periodic ticker, or extra monitor thread is needed.
#include <IOKit/IOLib.h>

extern void boot_log_tick(unsigned now);
void amethyst_boot_log_start(void);

void amethyst_boot_log_start(void)
{
	IOLog("AmethystBootLog: BSD hook calling tick directly\n");
	boot_log_tick(0);
	IOLog("AmethystBootLog: tick returned\n");
}
