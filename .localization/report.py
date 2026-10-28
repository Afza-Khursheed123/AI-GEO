from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]/'AIGEOTOOLS'
modified = subprocess.run(['git', 'diff', '--name-only'], cwd=root, capture_output=True, check=True).stdout.decode().splitlines()
modified = [name for name in modified if name != 'requirements.txt']
groups = [('Application entry point', [n for n in modified if n == 'geo_tool.py']), ('UI modules', [n for n in modified if n.startswith('modules/ui/')]), ('Supporting modules', [n for n in modified if n.startswith('modules/') and not n.startswith('modules/ui/')]), ('Publishing helpers', [n for n in modified if n.startswith('platform_sync/')])]
report = '''# Native English interface

The application now uses English source strings by default. No browser translation, translation service, runtime translation API, language switcher or UI redesign was added.

## Changes

- Translated navigation, headings, tabs, sidebar settings, controls, help, examples, progress messages, errors and notifications.
- Translated chart/report labels, CSV column labels, download names, publishing instructions, clarification templates, Schema placeholders and generated output templates.
- Translated content-generation, optimization, evaluation, keyword, image and video prompts. Authoring prompts explicitly request English prose while retaining technical identifiers and JSON field names.
- Replaced Chinese marketing word banks and query patterns with English presets. Keyword combinations use spaces and place the subject inside complete English questions. The semantic-expansion fallback and negative-monitoring query templates also produce natural English queries.
- Adapted keyword length guidance to English words instead of Chinese character counts.
- Kept original provider aliases and legacy platform/workflow metadata readable through `modules/english_compat.py`. Normalization occurs on reads; existing database contents and schema are not migrated or rewritten. User-authored brand names, article text, keywords and documents are preserved.
- Preserved platform integrations, model identifiers, API endpoints, credentials handling, currencies, workflows and GEO capabilities.

## English-language compatibility changes to analysis

Scoring weights, arithmetic, thresholds and numeric constants are unchanged. English text matching now supports English terms and case-insensitive matching where needed. Original Chinese regular-expression alternatives, sentiment vocabulary and stop words remain for compatibility with existing content. Source verification recognizes English statements and report/data references. Provider aliases also preserve access to the existing model defaults and cost configuration.

Keyword assembly and fallback query wording were adapted for English grammar; combination choices, result limits, similarity thresholds and deduplication remain in place. These are language-compatibility changes, not new GEO scoring methods.

## Chinese intentionally retained

- Chinese provider/platform spellings in `modules/english_compat.py`: compatibility keys for configurations and records created by the original version. English labels are displayed.
- Chinese text-analysis vocabulary, Unicode ranges and regular-expression alternatives: recognize existing Chinese documents and model responses.
- Developer comments/docstrings and existing README/docs: not rendered application UI. The English help panel remains native English; linked original documentation is still in its original language.
- Existing user-authored content, stored articles, document filenames, brands and third-party/API response text: preserved as data rather than automatically translated.

No untranslated static Chinese UI strings were found by the final source audit. The regression suite scans ordinary source strings, including f-strings, excluding documented compatibility data, regular expressions and developer docstrings. It also checks rendered UI text.

## Validation

- Python syntax compilation of `geo_tool.py`, `modules/`, `platform_sync/` and `tests/`: passed.
- `python -m unittest discover -s tests -v`: 16 tests passed.
- Streamlit AppTest: initial render, all 11 main tabs, keyword-builder interaction and result generation, plus populated article/history/optimization/validation/cost-report views passed without application exceptions or error messages.
- SQLite and JSON storage round trips, legacy metadata and provider aliases, keyword presets/fallbacks, English sentiment/source detection, prompt variable formatting, response parsing and regex compilation passed.
- Compared all 48 existing Python files against the original revision: no existing class or function removed. Numeric constants in scoring/metrics/ROI/similarity modules are unchanged. All `CREATE TABLE` statements are identical.
- `git diff --check`: passed.

Live model calls and external publishing were not exercised; these require credentials and would make external requests. Existing Streamlit deprecation/bare-mode warnings appeared during AppTest. No dependency versions were changed for this task. The pre-existing local change to `requirements.txt` was left untouched.

## Restart on this machine

Stop the running Streamlit process with **Ctrl+C**, then run in PowerShell:

```powershell
cd "D:\\7 sem\\madcep\\AIGEOTOOLS"
& "..\\.venv\\Scripts\\python.exe" -m streamlit run geo_tool.py
```

Open the local URL printed by Streamlit and refresh the browser. Existing API settings and data can continue to be used. Previously generated Chinese articles remain unchanged; newly generated prose is requested in English.

To repeat validation from the repository directory:

```powershell
& "..\\.venv\\Scripts\\python.exe" -m compileall -q geo_tool.py modules platform_sync tests
& "..\\.venv\\Scripts\\python.exe" -m unittest discover -s tests -v
```

## Files modified

'''
for title, names in groups:
    report += '### '+title+'\n\n'+'\n'.join('- `'+name+'`' for name in names)+'\n\n'
report += '### Files added\n\n- `modules/english_compat.py` — legacy metadata/provider compatibility.\n- `tests/test_english_interface.py` — offline regression and Streamlit smoke tests.\n- `ENGLISH_INTERFACE.md` — this change report and restart instructions.\n'
(root/'ENGLISH_INTERFACE.md').write_text(report, encoding='utf-8')
print(f'Report written: {len(modified)} modified source files and 3 added files.')
