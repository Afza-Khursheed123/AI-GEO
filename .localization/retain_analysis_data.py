import ast
import pathlib
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]/'AIGEOTOOLS'
for filename, names in [('content_uniqueness.py', {'stop_words'}), ('ai_search_verifier.py', {'positive_words', 'negative_words'})]:
    p = root/'modules'/filename
    original = subprocess.run(['git', 'show', 'HEAD:modules/'+filename], cwd=root, capture_output=True, check=True).stdout.decode('utf-8')
    values = {n.targets[0].id: ast.get_source_segment(original, n.value) for n in ast.walk(ast.parse(original)) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in names}
    source = p.read_text(encoding='utf-8')
    for name, value in values.items():
        tree = ast.parse(source)
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name:
                lines = source.splitlines(keepends=True)
                first = sum(map(len, lines[:n.value.lineno-1])) + len(lines[n.value.lineno-1].encode()[:n.value.col_offset].decode())
                last = sum(map(len, lines[:n.value.end_lineno-1])) + len(lines[n.value.end_lineno-1].encode()[:n.value.end_col_offset].decode())
                source = source[:first] + value + source[last:]
                break
    source = source.replace('"Medium 1/3"', '"Middle 1/3"')
    p.write_text(source, encoding='utf-8')
