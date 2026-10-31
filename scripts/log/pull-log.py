#!/usr/bin/env python3
"""Pull the Amethyst diagnostic log (sheng-log=1) off the phone and decode it.

Why this exists: Amethyst has no usable serial console, so a boot could only be
inspected by photographing the screen. With BootLog.c linked in and sheng-log=1
on the boot command line, the kernel now stores its message buffer into the log
window, and this script reads it back over ADB in LineageOS Recovery.

The window is the last 32 MiB of the *unixnu* partition -- not userdata, so
Android's data is never touched. Unlike asteroids' puller, the partition is
found by name from the recovery shell rather than hardcoded, because this device
keeps its root image in a split partition.

Nothing is written to the phone: the 32 MiB copy goes to /tmp (RAM) and comes
back with `adb pull`.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
DECODER = KIT / 'sheng' / 'read-sheng-log.py'
BLOCK = 4096
LOG_BLOCKS = 8192  # NativeUfs kLogReserveBlocks
PARTITION = 'unixnu'


def adb(*args, check=True):
    return subprocess.run(['adb', *args], check=check, capture_output=True).stdout


def partition_bounds(name):
    """First LBA and block count of a partition, from the recovery shell.

    Accepts either the by-name symlink or the GPT table; recovery exposes
    /dev/block/by-name but not always a partition table dump.
    """
    raw = adb('shell', f'readlink -f /dev/block/by-name/{name}').decode().strip()
    match = re.search(r'/dev/block/(?:sd[a-z]|mmcblk\d+|nvme\d+n\d+p?)(\d+)$', raw)
    if not match:
        sys.exit(f'{name} resolves to {raw!r}, which has no partition number')
    number = match.group(1)
    # The kernel exposes the start and size of a named partition in sysfs.
    base = f'/sys/class/block/$(basename $(readlink -f /dev/block/by-name/{name}))'
    start = adb('shell', f'cat /sys/class/block/*{name}*/start 2>/dev/null || '
                         f'cat {base}/start').decode().strip()
    size = adb('shell', f'cat /sys/class/block/*{name}*/size 2>/dev/null || '
                        f'cat {base}/size').decode().strip()
    try:
        return int(start), int(size)
    except ValueError:
        sys.exit(f'could not read start/size for {name}: '
                 f'start={start!r} size={size!r} (partition {number})')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True, type=Path,
                    help='directory for log.bin and the decoded text')
    ap.add_argument('--partition', default=PARTITION)
    ap.add_argument('--device', default=None,
                    help='block device to read instead of looking up the partition')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if adb('shell', 'id -u').decode().strip() != '0':
        sys.exit('adb shell is not root: enable ADB in LineageOS Recovery')

    if args.device:
        skip = None
        region = args.device
    else:
        start, blocks = partition_bounds(args.partition)
        if blocks < LOG_BLOCKS:
            sys.exit(f'{args.partition} has {blocks} blocks, smaller than the '
                     f'{LOG_BLOCKS}-block log window')
        # The window is the last LOG_BLOCKS blocks of the partition.
        skip = start + blocks - LOG_BLOCKS
        region = f'/dev/block/by-name/{args.partition}'
        print(f'{args.partition}: start={start} blocks={blocks} '
              f'-> log at LBA {skip}..{start + blocks - 1}')

    remote = '/tmp/amethyst-log.bin'
    command = f'dd if={region} of={remote} bs={BLOCK} count={LOG_BLOCKS} '
    if skip is not None:
        command += f'skip={skip} '
    # The shell can report 255 after dd finished (the link drops as the session
    # closes), so the copy is judged by its size, not by exit status.
    adb('shell', command + '2>/dev/null', check=False)
    copied = adb('shell', f'stat -c %s {remote} 2>/dev/null', check=False).decode().strip()
    if copied != str(LOG_BLOCKS * BLOCK):
        sys.exit(f'the copy in {remote} has {copied or "no"} bytes, '
                 f'not {LOG_BLOCKS * BLOCK}')
    log = args.out / 'log.bin'
    adb('pull', remote, str(log))
    adb('shell', f'rm -f {remote}', check=False)
    if log.stat().st_size != LOG_BLOCKS * BLOCK:
        sys.exit(f'short read: {log.stat().st_size} of {LOG_BLOCKS * BLOCK} bytes')

    subprocess.run([sys.executable, str(DECODER), '--decode', str(log),
                    '--out', str(args.out)], check=True)
    latest = args.out / 'latest.txt'
    if latest.exists():
        print(f'\n--- {latest} (last lines) ---')
        print('\n'.join(latest.read_text(errors='replace').splitlines()[-40:]))


if __name__ == '__main__':
    main()
