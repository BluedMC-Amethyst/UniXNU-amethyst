#!/usr/bin/env python3
"""Compile the generated stand-in definitions with the kernel's own recipe.

Mirrors build-log.py: replay the recorded osfmk startup.c command, swapping in
our source. Only the -o target changes, so the flags are exactly the ones the
kernel uses for this kind of C file (-mgeneral-regs-only, -Wall -Wextra, ...).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = Path(__file__).resolve().parent
# The built XNU tree lives beside this repository, not inside it.
TREE = ROOT.parent / 'UniXNU/out/amethyst/ipados-17.7.11-21H461/amethyst/tree'
RECIPE = TREE / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/osfmk/DEVELOPMENT/startup.o.json'


def build(source_name, obj_name):
    record = json.loads(RECIPE.read_text().strip().rstrip(','))
    args = list(record['arguments'])
    source = str(KIT / source_name)
    args = [source if arg == record['file'] else arg for arg in args]
    args[args.index('-o') + 1] = str(KIT / obj_name)
    # -Werror is dropped: generated stand-ins legitimately trigger
    # -Wmissing-prototypes (they have no declaration in this unit).
    args = [arg for arg in args if arg != '-Werror']
    args += ['-DXNU_BOOT_PROGRESS=1', '-I' + str(TREE / '.cache/xnu-work/osfmk'), '-I' + str(KIT)]
    result = subprocess.run(args, cwd=record['directory'], capture_output=True, text=True)
    (KIT / (Path(obj_name).stem + '-compile.log')).write_text(result.stdout + result.stderr)
    errors = [line for line in (result.stdout + result.stderr).splitlines() if 'error:' in line]
    if result.returncode:
        raise SystemExit(f'{source_name} failed:\n' + '\n'.join(errors[:20]))
    obj = KIT / obj_name
    symbols = subprocess.run(['llvm-nm', str(obj)], capture_output=True, text=True).stdout
    defined = [line for line in symbols.splitlines() if len(line.split()) >= 3]
    print(f'PASS {source_name} -> {obj_name}: {len(defined)} symbols, {obj.stat().st_size} bytes')
    return obj


if __name__ == '__main__':
    build('BootLogStubsGenerated.c', 'BootLogStubsGenerated.o')
