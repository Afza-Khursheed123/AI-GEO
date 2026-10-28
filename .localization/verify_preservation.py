import ast
import pathlib
import subprocess

root = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
files = [root/'geo_tool.py', *root.joinpath('modules').rglob('*.py'), *root.joinpath('platform_sync').rglob('*.py')]
checked = 0
for p in files:
    result = subprocess.run(['git', 'show', 'HEAD:'+p.relative_to(root).as_posix()], cwd=root, capture_output=True)
    if result.returncode:
        continue
    old = ast.parse(result.stdout.decode('utf-8'))
    new = ast.parse(p.read_text(encoding='utf-8'))
    names = lambda t: {n.name for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    assert names(old) <= names(new), p
    if p.name in ['content_scorer.py', 'content_metrics.py', 'eeat_enhancer.py', 'fact_density_enhancer.py', 'roi_analyzer.py', 'content_uniqueness.py']:
        numbers = lambda t: [n.value for n in ast.walk(t) if isinstance(n, ast.Constant) and type(n.value) in (int, float)]
        assert numbers(old) == numbers(new), ('numeric scoring constants', p)
    if p.name == 'data_storage.py':
        ddl = lambda t: [n.value for n in ast.walk(t) if isinstance(n, ast.Constant) and isinstance(n.value, str) and 'CREATE TABLE' in n.value]
        assert ddl(old) == ddl(new), 'database DDL changed'
    checked += 1
print(f'Preservation checks passed for {checked} existing Python files: all functions/classes retained, scoring constants unchanged, database DDL identical.')
