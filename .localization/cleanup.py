import pathlib
import re
import subprocess

root = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
diff = subprocess.run(['git', 'diff', '--unified=0', '--', '*.py'], cwd=root, capture_output=True, check=True).stdout.decode('utf-8')
changed = {}
filename = None
line_number = 0
for line in diff.splitlines():
    if line.startswith('+++ b/'):
        filename = line[6:]
    elif line.startswith('@@'):
        line_number = int(re.search(r'\+(\d+)', line)[1])
    elif line.startswith('+') and filename:
        changed.setdefault(filename, set()).add(line_number)
        line_number += 1
    elif line.startswith(' '):
        line_number += 1
for name, numbers in changed.items():
    p = root/name
    lines = p.read_text(encoding='utf-8').splitlines()
    for number in numbers:
        lines[number-1] = lines[number-1].rstrip()
    p.write_text('\n'.join(lines)+'\n', encoding='utf-8')
