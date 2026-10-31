#!/usr/bin/env python3
"""Generate the remaining weak stand-ins BootLog.c needs on a board that does not
build sheng's probes.

BootLog.c reads every optional diagnostic through a weak reference
(`__attribute__((weak_import))`). On a static kernel link each one still needs a
definition, or the link fails. UniXNU-asteroids ships BootLogStandins.c for the
same purpose, but that file was generated against a newer sheng build and misses
94 of the symbols our BootLog.c imports (adreno buffer/diag arrays, the legacy
display probe arrays, cpufreq, keyevents, mic, boot_progress renderer buffers).

This script does not hand-copy anything: it parses BootLog.c's own declarations
and emits a definition of the identical type for every still-undefined symbol.
Every definition is weak, so a real driver's symbol always wins; they all read as
zero/empty, and the log simply prints those rows empty.

Alignment note: the declaration type is reproduced exactly, so `nm`-level and
size checks downstream match what BootLog.c expects. Function pointers are
emitted as NULL, not as stub functions, so a weak test like `if (fn)` in
BootLog.c stays false, which is what "not available" means to it.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = Path(__file__).resolve().parent
BOOTLOG = KIT / 'BootLog.c'
OUTPUT = KIT / 'BootLogStubsGenerated.c'

# Declarations that this log's writer reads; parsed straight out of BootLog.c.
DECL = re.compile(r'^extern\s+(.*?)\s*__attribute__\(\(weak_import\)\)\s*;?\s*$')
# A second declarator sharing the attribute: `a, b __attribute__((weak_import));`
TAIL = re.compile(r',\s*([A-Za-z_]\w*)\s*$')
# A function pointer: `int (*name)(uint64_t, uint32_t *)`
QUALIFIERS = ('volatile', 'const', 'unsigned', 'signed')
FNPTR = re.compile(r'^(.*?)\s*\(\s*\*\s*([A-Za-z_]\w*)\s*\)\s*(\(.*\))$')


def split_declarators(text):
    """Split a declarator list on commas that are not inside parentheses.

    Parameter lists contain commas (`(char *, unsigned)`), so a plain split
    would cut a function declarator in half.
    """
    pieces, depth, current = [], 0, []
    for character in text:
        if character == '(':
            depth += 1
        elif character == ')':
            depth -= 1
        if character == ',' and depth == 0:
            pieces.append(''.join(current))
            current = []
        else:
            current.append(character)
    pieces.append(''.join(current))
    return pieces


def parse_declarations(text):
    """Every `extern <type> <name> ... __attribute__((weak_import));` in the file.

    Returns {name: (type_text, stars, params)} so the exact type can be reused.
    Handles the three shapes BootLog.c uses:
      extern volatile uint64_t a, b __attribute__((weak_import));   (shared attribute)
      extern volatile uint32_t a __attribute__((weak_import)), b __attribute__((weak_import));
      extern int (*fn)(uint64_t, uint32_t *) __attribute__((weak_import));
    """
    found = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('extern ') or 'weak_import' not in line:
            continue
        # Drop the attributes and the statement terminator; what remains is
        # `<type words> <declarator list>`.
        bare = re.sub(r'\s*__attribute__\(\(weak_import\)\)', '', line)
        bare = bare[len('extern '):].rstrip(';').strip()

        # Function pointer form: type is everything before `(*name)`.
        fn = FNPTR.match(bare)
        if fn:
            type_text, name, params = fn.groups()
            found[name] = (type_text.strip(), 'FP', params)
            continue

        # The type is the leading qualifiers plus exactly one type name, or
        # `struct <tag>`. The declarator text follows; it may sit next to `(`
        # with no space, so the type is matched directly rather than by words.
        # `\b` alone would let the name join the type, so the split is explicit.
        qualifiers = r'(?:(?:volatile|const|unsigned|signed)\s+)*'
        # A function returning a pointer: `const char *name(args)`.
        pointer_fn = re.match(
            rf'^((?:{qualifiers})?(?:struct\s+\w+|[A-Za-z_]\w*))\s*\*\s*([A-Za-z_]\w*\s*\(.*)$',
            bare.replace(' *', '*'))
        if pointer_fn:
            type_text, declarator = pointer_fn.groups()
            type_text = type_text.strip() + ' *'
            function = re.match(r'^([A-Za-z_]\w*)\s*(\(.*\))$', declarator.strip())
            if function:
                found[function.group(1)] = (type_text, 'FN', function.group(2))
                continue

        type_match = re.match(
            rf'^({qualifiers}(?:struct\s+\w+|[A-Za-z_]\w*))\s+([A-Za-z_]\w*.*)$', bare)
        if not type_match:
            # No declarator text after the type: a bare type is not useful here.
            continue
        type_text = type_match.group(1)
        rest = type_match.group(2)

        for piece in split_declarators(rest):
            piece = piece.strip()
            if not piece:
                continue
            name_match = re.match(r'^(\*?)\s*([A-Za-z_]\w*)\s*(.*)$', piece)
            if not name_match:
                continue
            stars, name, suffix = name_match.groups()
            suffix = suffix.strip()
            # A trailing parenthesised list means this is a function, not a
            # variable: `unsigned boot_ui_trace_hot_rows(char *, unsigned)`.
            if suffix.startswith('('):
                found[name] = (type_text, 'FN', suffix)
            else:
                found[name] = (type_text, stars, suffix)
    return found


def emit_function(name, type_text, params):
    """A weak no-op that reports "not available": 0 rows, or NULL for a string.

    BootLog.c guards each of these with `if (&fn)`, so a definition is needed to
    link, but returning zero means it formats an empty row, exactly as if the
    probe had never run.
    """
    if type_text == 'const char *' or type_text.endswith('*'):
        return f'WEAK {type_text} {name}{params} {{ return 0; }}'
    if type_text == 'void':
        return f'WEAK void {name}{params} {{ (void)0; }}'
    return f'WEAK {type_text} {name}{params} {{ return 0; }}'


def emit(name, type_text, stars, suffix):
    """A weak definition of the exactly-declared type."""
    if stars == 'FP':
        # Function pointer variable, initialised to NULL so `if (fn)` reads false.
        return f'WEAK {type_text} (*{name}){suffix} = 0;'
    if stars == 'FN':
        # A real function: a weak no-op returning "not available" (0 / NULL).
        return emit_function(name, type_text, suffix)
    if suffix or stars:
        # Arrays and plain pointers all zero-initialise.
        declarator = f'*{name}' if stars else name
        return f'WEAK {type_text} {declarator} {suffix};'
    return f'WEAK {type_text} {name};'


def main():
    text = BOOTLOG.read_text()
    declarations = parse_declarations(text)

    # Which names are still undefined? Ask the object itself, so this does not
    # depend on a link log that a later relink would overwrite.
    imported = subprocess.run(
        ['llvm-nm', '-u', str(KIT / 'BootLog.o')], capture_output=True, text=True, check=True)
    undefined = {line.split()[-1].lstrip('_') for line in imported.stdout.splitlines() if line.strip()}

    # Everything undefined that BootLog.c itself declares with a weak_import
    # type. A plain `extern` declaration means the symbol belongs to a real
    # driver or the kernel (thread_deallocate, vm_kernel_slide, ...): stubbing
    # those would shadow genuine implementations, so only weak_import
    # declarations are stubbed. parse_declarations records exactly those.
    targets = sorted(name for name in undefined if name in declarations)
    missing = sorted(name for name in undefined if name not in declarations)
    if missing:
        # Not a hard error: some are defined by real drivers we build. Report them.
        print('still undefined, provided elsewhere (driver or kernel):')
        for name in missing:
            print('   ', name)

    lines = [
        '// SPDX-License-Identifier: BSD-2-Clause-Patent',
        '// GENERATED by gen-standins.py from BootLog.c declarations. Do not edit.',
        '//',
        '// Weak zero definitions for every optional diagnostic BootLog.c reads but',
        '// that this board does not build. Each type is copied verbatim from the',
        "// writer's own declaration, so sizes and alignment match; a real driver's",
        '// symbol, when linked, overrides all of them.',
        '#include <stdint.h>',
        '#include <stddef.h>',
        '// The record layouts BootLog.c declares for its arrays.',
    ]
    # Copy the struct definitions the declarations refer to, verbatim, so the
    # generated definitions use the identical layout.
    for struct_line in re.findall(r'^struct\s+\w+\s*\{.*\};$', text, re.M):
        lines.append(struct_line)
    lines += [
        '// The audio ABI header BootLog.c includes for its one diagnostic pointer.',
        '#include "ShengAudioAbi.h"',
        '',
        '#define WEAK __attribute__((weak))',
        '',
    ]
    for name in targets:
        type_text, stars, suffix = declarations[name]
        lines.append(emit(name, type_text, stars, suffix))
    OUTPUT.write_text('\n'.join(lines) + '\n')
    print(f'wrote {OUTPUT} with {len(targets)} definitions')


if __name__ == '__main__':
    main()
