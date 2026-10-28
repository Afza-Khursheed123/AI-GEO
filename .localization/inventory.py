import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
files = [ROOT / 'geo_tool.py', *ROOT.joinpath('modules').rglob('*.py'), *ROOT.joinpath('platform_sync').rglob('*.py')]
segments = set()
for p in files:
    tree = ast.parse(p.read_text(encoding='utf-8'))
    docs = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs:
            segments.update(re.findall(r'[\u3400-\u9fff]+', n.value))
pathlib.Path(__file__).with_name('segments.txt').write_text('\n'.join(sorted(segments)), encoding='utf-8')
print(len(segments))
