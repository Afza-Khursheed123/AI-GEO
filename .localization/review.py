import ast
import pathlib
import sys
root = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
for filename in sys.argv[1:]:
    p = root / filename
    t = ast.parse(p.read_text(encoding='utf-8'))
    docs = {id(n.value) for n in ast.walk(t) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    print(filename)
    for n in sorted(ast.walk(t), key=lambda n: getattr(n, 'lineno', 0)):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs and len(n.value) > 35:
            print(f'{n.lineno}: {n.value}')
