"""Development-only source localization. No translation service or runtime hook."""
import ast
import io
import pathlib
import re
import subprocess
import tokenize
import os

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
mapping = dict(line.split('\t', 1) for line in pathlib.Path(__file__).with_name('translations.tsv').read_text(encoding='utf-8').splitlines() if '\t' in line)
han = re.compile(r'[\u3400-\u9fff]+')
punctuation = str.maketrans({'，': ', ', '。': '. ', '；': '; ', '：': ': ', '（': ' (', '）': ')', '、': ', ', '？': '?', '！': '!', '「': '“', '」': '”'})

def translate(text, raw=False):
    def sub(m):
        value = mapping.get(m[0], m[0])
        if value == m[0]:
            return value
        before, after = text[:m.start()], text[m.end():]
        if before and (before[-1].isascii() and before[-1].isalnum() or before[-1] == '}'):
            value = ('\\s*' if raw else ' ') + value
        if after and (after[0].isascii() and after[0].isalnum() or after[0] == '{'):
            value += '\\s*' if raw else ' '
        return value
    result = han.sub(sub, text)
    if not raw:
        result = result.translate(punctuation)
        result = re.sub(r'(?<=\d)(?=words|items|points)', ' ', result)
        result = result.replace('12-28 words', '5-12 words').replace('12–28 words', '5–12 words')
        result = result.replace('BBilibili', 'Bilibili')
    return result

files = [ROOT/'geo_tool.py', *ROOT.joinpath('modules').rglob('*.py'), *ROOT.joinpath('platform_sync').rglob('*.py')]
for p in files:
    if os.environ.get('LOCALIZE_ONLY') and p.name != os.environ['LOCALIZE_ONLY']:
        continue
    rel = p.relative_to(ROOT).as_posix()
    source = subprocess.run(['git', 'show', 'HEAD:'+rel], cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
    tree = ast.parse(source)
    docs = {(n.value.lineno, n.value.col_offset) for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)}
    tokens = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in (tokenize.STRING, tokenize.FSTRING_MIDDLE) and token.start not in docs and han.search(token.string):
            raw = token.type == tokenize.STRING and bool(re.match(r'(?i)[ubf]*r', token.string))
            new = translate(token.string, raw)
            if token.type == tokenize.FSTRING_MIDDLE:
                if han.match(token.string):
                    new = ' ' + new
                if han.search(token.string[-1:]):
                    new += ' '
            token = token._replace(string=new)
        tokens.append(token)
    result = tokenize.untokenize(tokens)
    compile(result, rel, 'exec')
    p.write_text(result, encoding='utf-8')
