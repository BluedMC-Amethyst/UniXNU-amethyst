#!/usr/bin/env python3
"""A zero-slot startup snapshot must decode without the periodic writer."""
import runpy
import tempfile
from pathlib import Path

kit = Path(__file__).resolve().parent
decoder = runpy.run_path(str(kit / 'sheng/read-sheng-log.py'))
scratch = kit.parents[2] / '.scratch'
message = b'BSD startup snapshot\n'
values = dict.fromkeys(decoder['FIELDS'], 0)
values.update(magic=b'SHLOG001', version=4, header_bytes=148, boot_id=1,
              first_lba=124206848, window_blocks=8192, msg_first=1,
              msg_blocks=32, msg_bytes=len(message), slot_first=33,
              slot_blocks=16, slot_count=509, state=1, tag=b'bsd-startup')
blob = bytearray(33554432)
decoder['HEADER'].pack_into(blob, 0, *(values[n] for n in decoder['FIELDS']))
blob[4096:4096 + len(message)] = message
with tempfile.TemporaryDirectory(dir=scratch, prefix='snapshot-check-') as tmp:
    run = decoder['decode'](blob, Path(tmp))
    assert (run / 'msgbuf.txt').read_bytes() == message
    assert (run / 'slots.txt').read_text() == ''
print('PASS: startup message buffer decodes with zero periodic slots')
