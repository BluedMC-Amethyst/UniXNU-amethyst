#!/usr/bin/env python3
"""Check the string stand-in consumed unconditionally by the log writer."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('standins', Path(__file__).with_name('gen-standins.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.emit_function('boot_progress_tag', 'const char *', '(void)') == (
    'WEAK const char * boot_progress_tag(void) { return ""; }')
print('PASS: boot_progress_tag stand-in returns an empty string, not NULL')
