#!/usr/bin/env python3
"""Panic records must survive the machine halting.

panic() formats its text and calls PE_panic_hook() with interrupts off, before
the halt, while the writer's next snapshot is up to a period away. BootLog.c
chains that hook and writes the panic text synchronously. This check builds a
synthetic record in the message region and asserts the decoder surfaces it,
without needing a device.
"""
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLOCK, LOG_BLOCKS = 4096, 8192
HEADER = struct.Struct('<8sIIQQ8I6I32s')
UNPACK = struct.Struct('<8sIIQIIII')          # must match BootLog.c boot_log_panic_header
TEXT = b'Kernel data abort.\nFar: 0xfffffff009123456\n'
TAIL = b'[  34.594719]: AmethystBootLog: window first=124206848 blocks=8192\n'

blob = bytearray(BLOCK * LOG_BLOCKS)
HEADER.pack_into(blob, 0, b'SHLOG001', 4, HEADER.size, 0xdeadbeef, 124206848, LOG_BLOCKS,
                 1, 32, 0, 33, 16, 509, 1, 0, 1, 0, 1, 1, 2, b'')
struct.pack_into('<4I', blob, HEADER.size, 0, 65536, 0, 0)
struct.pack_into('<I', blob, HEADER.size + 16, 65536)
struct.pack_into('<II', blob, HEADER.size + 20, 0, 0)

region = bytearray(32 * BLOCK)
UNPACK.pack_into(region, 0, b'SHLOGPN1', 1, UNPACK.size, 0xdeadbeef, len(TEXT), 1, 1, 1)
region[UNPACK.size:UNPACK.size + len(TEXT)] = TEXT
at = UNPACK.size + len(TEXT)
region[at:at + len(TAIL)] = TAIL
blob[BLOCK:BLOCK + 32 * BLOCK] = region

source = (HERE / 'BootLog.c').read_text()
assert 'PE_arm_debug_panic_hook = boot_log_panic_record;' in source
assert 'boot_log_prev_panic_hook = PE_arm_debug_panic_hook;' in source, 'previous hook must be preserved'
assert '__atomic_exchange_n(&boot_log_panic_fired, 1, __ATOMIC_ACQ_REL)' in source, 'must run once only'
assert 'boot_log_install_panic_hook();' in source, 'hook must be installed at startup'

with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp)
    (out / 'log.bin').write_bytes(bytes(blob))
    r = subprocess.run([sys.executable, str(HERE / 'sheng' / 'read-sheng-log.py'),
                        '--decode', str(out / 'log.bin'), '--out', str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    run = out / 'untagged-deadbeef'
    assert (run / 'panic.txt').read_bytes() == TEXT
    assert (run / 'msgbuf.txt').read_bytes() == TAIL.rstrip(b'\0')
    assert 'PANIC RECORD wrote=1 synced=1' in r.stdout, r.stdout
print('PASS: panic text and pre-panic messages decode from a record written during panic')
