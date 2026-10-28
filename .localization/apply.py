import pathlib
import re
ROOT = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
mapping = dict(line.split('\t', 1) for line in pathlib.Path(__file__).with_name('translations.tsv').read_text(encoding='utf-8').splitlines() if '\t' in line)
files = [ROOT / 'geo_tool.py', *ROOT.joinpath('modules').rglob('*.py'), *ROOT.joinpath('platform_sync').rglob('*.py')]
for p in files:
    source = p.read_text(encoding='utf-8')
    translated = re.sub(r'[\u3400-\u9fff]+', lambda m: mapping.get(m[0], m[0]), source)
    if source != translated:
        p.write_text(translated, encoding='utf-8')
