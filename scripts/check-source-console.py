#!/usr/bin/env python3
"""Run the patched PE_create_console with host stubs. Usage: script XNU_SOURCE OUTPUT_DIR."""
from pathlib import Path
import subprocess
import sys

source = Path(sys.argv[1]) / 'pexpert/arm/pe_init.c'
text = source.read_text()
start = text.index('void\nPE_create_console(void)')
end = text.index('\nint\nPE_current_console', start)
function = text[start:end]
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
test = out / 'console-check.c'
test.write_text('''#include <assert.h>
#include <string.h>
typedef int boolean_t;
#define FALSE 0
enum { kPEGraphicsMode=1, kPETextMode=2 };
struct { struct { int v_display; } video; } PE_state;
static int requested, actual, checked;
static void check_for_panic_log(void) { checked=1; }
static int PE_parse_boot_argn(const char *s, void *p, unsigned long n) {
  assert(!strcmp(s,"-textconsole") && n==sizeof(boolean_t));
  *(boolean_t *)p=requested; return requested;
}
static void PE_initialize_console(void *p, int mode) {
  assert(checked && p==&PE_state.video); actual=mode;
}
''' + function + '''
int main(void) {
  for (int display=0;display<2;display++) for (requested=0;requested<2;requested++) {
    PE_state.video.v_display=display; checked=0; actual=0;
    PE_create_console();
    assert(actual==(display && !requested ? kPEGraphicsMode : kPETextMode));
  }
}
''')
binary = out / 'console-check'
subprocess.run(['cc', '-Wall', '-Wextra', '-Werror', str(test), '-o', str(binary)], check=True)
subprocess.run([str(binary)], check=True)
print('PASS: actual patched console creation selects text immediately when requested; graphics default preserved')
