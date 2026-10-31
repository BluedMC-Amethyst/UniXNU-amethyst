#!/usr/bin/env python3
"""The panic hook must not touch the UFS device.

Both UFS entry points reach lck_mtx_lock and then a blocking SCSI command:

  native_ufs_log_write -> hostWrite4k -> lck_mtx_lock, hostScsiDir
  native_ufs_log_sync  ->                lck_mtx_lock, hostScsiDir

In a panic handler that lock never falls free: the panicking CPU either already
holds it or the peer CPU is being parked. lck_mtx_lock then aborts with
"Mutex ... is unexpectedly owned by thread" at lock_mtx.c:175, which is itself
the first nested panic and destroys the evidence for the original fault.

boot_log_panic_record must therefore call neither. amethyst_boot_log_flush is the
safe persistence path: normal thread context, try-lock, and it is called from
boot threads rather than panic context.
"""
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = (root / 'log/BootLog.c').read_text()

# Isolate boot_log_panic_record and strip comments, so prose that names the
# banned functions does not trip the check.
start = src.index('static void boot_log_panic_record')
body = src[start:]
end = body.index('\n}\n')
body = body[:end]
code = re.sub(r'//[^\n]*', '', body)

for banned in ('native_ufs_log_write', 'native_ufs_log_sync',
               'IOLockLock', 'IOSleep', 'hostScsiDir'):
    assert banned not in code, f'panic hook must not call {banned}'

# It still chains the previous hook, so the panic is not swallowed.
assert 'boot_log_prev_panic_hook' in code

# The safe flush path still syncs, and it is not called from the hook.
flush = src[src.index('int amethyst_boot_log_flush'):]
flush = flush[:flush.index('\n}\n')]
assert 'native_ufs_log_sync' in flush
assert 'IOLockTryLock' in flush, 'flush must stay non-blocking'

# Pin the premise in the shipped kernel: both entry points really lock.
dis_path = root / '.scratch/ufs-audit/kernel-guard.dis'
if dis_path.exists():
    locked = set()
    cur = None
    for line in open(dis_path, errors='replace'):
        if line.startswith('fffffff') and '>:' in line:
            m = re.search(r'<([^>]+)>:', line)
            cur = m.group(1) if m else None
            continue
        if cur and 'bl' in line and 'lck_mtx_lock' in line:
            locked.add(cur)
    for fn in ('_native_ufs_log_write', '_native_ufs_log_sync',
               '__ZN12_GLOBAL__N_111hostWrite4kEhyjPKvb'):
        assert fn in locked, f'{fn} was expected to take lck_mtx_lock'

print('PASS: panic hook does no blocking UFS work; only the flush path syncs')
