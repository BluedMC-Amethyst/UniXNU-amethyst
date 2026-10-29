#!/usr/bin/env python3
"""Check compiled Amethyst DTB export policy. Usage: script UNIXNU_ROOT DTB."""
import pathlib
import sys
import tomllib

device = pathlib.Path(__file__).resolve().parents[1]
board = tomllib.loads((device / 'board.toml').read_text())
args = board['payload']['kernel_args']
for key, value in [('native-ufs-root', '1'), ('sheng-data-persist', '0'), ('sheng-log', '0')]:
    assert [a for a in args if a.startswith(key + '=')] == [key + '=' + value]
assert board['payload']['adt']['persistent_data'] is False
assert 'CONFIG_XNU_NATIVE_UFS=y' in (device / 'configs/amethyst_defconfig').read_text().splitlines()

sys.path.insert(0, str(pathlib.Path(sys.argv[1]).resolve() / 'scripts'))
from unixnu.devicetree import hardware_properties, read_fdt

root = read_fdt(pathlib.Path(sys.argv[2]).read_bytes())
entries = list(root.walk())
handles = {n.scalar('phandle'): n for n in entries if 'phandle' in n.properties}
pmic = next(n for n in entries if n.name == 'pmic@0')
rtc = next(n for n in entries if n.name == 'rtc@6100')
assert pmic.cells('reg') == [0, 0]
assert rtc.cells('reg') == [0x6100, 0x6200]
assert all('unixnu,adt-name' not in n.properties for n in (pmic, rtc))
exports = [n for n in entries if 'unixnu,adt-name' in n.properties and n.enabled()]
assert any(n.strings('unixnu,adt-name') == ['spmi'] for n in exports)
for entry in exports:
    hardware_properties(entry, handles)
print('PASS: SPMI controller exports valid MMIO; PMIC/RTC bus-local regs remain unexported')
print('PASS: UFS root enabled exactly once; persistent Data/log and ADT persistence disabled')
