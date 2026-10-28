import ast
import io
import pathlib
import re
import subprocess
import tokenize

root = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
mapping = dict(line.split('\t', 1) for line in pathlib.Path(__file__).with_name('translations.tsv').read_text(encoding='utf-8').splitlines() if '\t' in line)
overrides = {'问题': 'problems?|issues?', '显示': 'shows?', '表明': 'indicates?', '报告': 'reports?', '研究': 'research|studies', '数据': 'data', '步骤': 'steps?', '第': 'step', '总结': 'summary|summarize', '结论': 'conclusions?', '例子': 'examples?', '应用': 'applications?', '目前': 'currently', '标准': 'standards?', '参考': 'reference|according to', '规范': 'specifications?|standards?', '符合': 'complies with', '不': 'not', '有': 'has|have', '存在': 'has|have', '好': 'good', '行': 'working', '指出': 'notes?|states?', '数据表明': 'data indicates', '数据要准确': 'keep data accurate'}
for p in [root/'geo_tool.py', *root.joinpath('modules').rglob('*.py'), *root.joinpath('platform_sync').rglob('*.py')]:
    if p.name == 'english_compat.py':
        continue
    original = subprocess.run(['git', 'show', 'HEAD:'+p.relative_to(root).as_posix()], cwd=root, capture_output=True, check=True).stdout.decode('utf-8')
    original_raw = [t.string for t in tokenize.generate_tokens(io.StringIO(original).readline) if t.type == tokenize.STRING and re.match(r'(?i)[ubf]*r', t.string)]
    index = 0
    tokens = []
    current_count = sum(t.type == tokenize.STRING and bool(re.match(r'(?i)[ubf]*r', t.string)) for t in tokenize.generate_tokens(io.StringIO(p.read_text(encoding='utf-8')).readline))
    if current_count != len(original_raw):
        print('SKIP raw mismatch', p.name, len(original_raw), current_count)
        continue
    for token in tokenize.generate_tokens(io.StringIO(p.read_text(encoding='utf-8')).readline):
        if token.type == tokenize.STRING and re.match(r'(?i)[ubf]*r', token.string):
            raw = original_raw[index]
            index += 1
            if re.search(r'[\u3400-\u9fff]', raw):
                def sub(m):
                    before = raw[:m.start()]
                    if before.rfind('[') > before.rfind(']'):
                        return m[0]
                    english = overrides.get(m[0], mapping.get(m[0], m[0]))
                    if english == m[0]:
                        return m[0]
                    english = english.replace(' ', r'\s+').replace("'", r"\'")
                    return '(?:'+m[0]+r'|\s*(?:'+english+r')\s*)'
                token = token._replace(string=re.sub(r'[\u3400-\u9fff]+', sub, raw))
        tokens.append(token)
    assert index == len(original_raw), (p, index, len(original_raw))
    source = tokenize.untokenize(tokens)
    compile(source, str(p), 'exec')
    p.write_text(source, encoding='utf-8')

for filename, names in [('ai_search_verifier.py', ['positive_words', 'negative_words']), ('negative_monitor.py', ['negative_keywords'])]:
    p = root/'modules'/filename
    original = subprocess.run(['git', 'show', 'HEAD:modules/'+filename], cwd=root, capture_output=True, check=True).stdout.decode('utf-8')
    old = ast.parse(original)
    source = p.read_text(encoding='utf-8')
    for name in names:
        for node in ast.walk(old):
            if not isinstance(node, ast.Assign):
                continue
            target = node.targets[0]
            if getattr(target, 'id', getattr(target, 'attr', None)) != name:
                continue
            values = ast.literal_eval(node.value)
            # Keep the existing Chinese lexicon for compatibility, plus idiomatic English.
            english = {'positive_words': ['excellent', 'outstanding', 'leading', 'recommended', 'preferred', 'best', 'powerful', 'efficient', 'innovative', 'professional', 'reliable', 'stable', 'exceptional'], 'negative_words': ['problem', 'issue', 'defect', 'limitation', 'failure', 'risk', 'warning', 'avoid', 'poor', 'slow', 'expensive', 'complex', 'difficult', 'unstable'], 'negative_keywords': ['drawback', 'limitation', 'defect', 'poor', 'negative review', 'complaint', 'negative', 'not recommended', 'pitfall', 'not worthwhile', 'failed', 'error', 'risk', 'bug', 'issue', 'problem', 'flaw', 'weakness', 'disadvantage']}[name]
            values = list(dict.fromkeys([v for v in values if re.search('[\u3400-\u9fff]', v)] + english))
            tree = ast.parse(source)
            for current in ast.walk(tree):
                if isinstance(current, ast.Assign) and getattr(current.targets[0], 'id', getattr(current.targets[0], 'attr', None)) == name:
                    lines = source.splitlines(keepends=True)
                    first = sum(map(len, lines[:current.value.lineno-1])) + len(lines[current.value.lineno-1].encode()[:current.value.col_offset].decode())
                    last = sum(map(len, lines[:current.value.end_lineno-1])) + len(lines[current.value.end_lineno-1].encode()[:current.value.end_col_offset].decode())
                    source = source[:first] + repr(values) + source[last:]
                    break
    p.write_text(source, encoding='utf-8')

# Editorial cleanup, including Markdown emphasis and translated word boundaries.
for p in [root/'geo_tool.py', *root.joinpath('modules').rglob('*.py'), *root.joinpath('platform_sync').rglob('*.py')]:
    s = p.read_text(encoding='utf-8')
    tokens = []
    for t in tokenize.generate_tokens(io.StringIO(s).readline):
        if t.type in (tokenize.STRING, tokenize.FSTRING_MIDDLE) and not re.match(r'(?i)[ubf]*r', t.string):
            value = t.string.replace('??', '?').replace('AI generationd', 'AI-generated').replace(': **', ':**')
            value = value.replace(')Expert', ') expert').replace(')Keyword strategist', ') keyword strategist')
            value = value.replace('You are a GEO expert and a highly rated', 'You are a GEO expert and a highly rated')
            value = value.replace('Help brands improve their visibility in AI given priority by models, credible mentions.', 'Help brands earn prominent, credible mentions in AI answers.')
            value = value.replace('Is it easy to AI extract and cite?', 'Can AI models easily extract and cite it?')
            value = value.replace('Whether in AI easy to recognize and mention in answers?', 'Can AI models recognize and mention it naturally?')
            value = value.replace('Is the brand name easy for AI Preferential mention?', 'Is the brand name easy for AI models to recognize and recommend?')
            t = t._replace(string=value)
        tokens.append(t)
    s = tokenize.untokenize(tokens)
    compile(s, str(p), 'exec')
    p.write_text(s, encoding='utf-8')
