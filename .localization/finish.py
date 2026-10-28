import ast
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
p = root/'geo_tool.py'
s = p.read_text(encoding='utf-8')
start = s.index('### 🎯 What is GEO?')
end = s.index('\n""")', start)
s = s[:start] + '''### 🎯 What is GEO?

**GEO (Generative Engine Optimization)** helps make your content visible in AI search answers.

Traditional SEO focuses on rankings in search engines such as Google and Baidu. GEO focuses on whether AI search services such as ChatGPT, Perplexity and Google SGE cite your brand and content when answering questions.

### 💡 Why use GEO?

When someone asks an AI assistant a question such as “What is the best software for my business?”, it retrieves information and generates an answer. High-quality, searchable content gives your brand a better chance of appearing in that answer.

**The goal of GEO** is to earn accurate, credible and prominent brand mentions in AI answers.

---

### 🔄 GEO workflow

| Stage | Feature | Purpose |
|------|------|------|
| 1️⃣ Keyword strategy | Keyword research | Create natural, long-tail queries for AI search |
| 2️⃣ Content creation | Article generation | Create structured, professional content using the knowledge base |
| 3️⃣ Content optimization | Article optimization | Enhance E-E-A-T and factual density, and generate Schema markup |
| 4️⃣ Validation | Multi-model validation | Check brand mentions across AI models |
| 5️⃣ Analysis | AI data reports | Track mention rates, ROI and competitor performance |
| 6️⃣ Distribution | Platform sync | Publish across platforms to expand searchable content |

---

### 📊 Core metrics

| Metric | Description |
|------|------|
| **Brand mention rate** | How often AI answers mention the brand |
| **E-E-A-T score** | Experience, expertise, authoritativeness and trustworthiness |
| **Factual density** | The density of verifiable information in the content |
| **Citation position** | Where the brand appears in an answer, with the first third preferred |

---

### 🌐 Supported platforms

**Publishing platforms (20+)**: Zhihu, Xiaohongshu, CSDN, Bilibili, GitHub, WeChat Official Accounts and others.

**AI validation providers (7)**: DeepSeek, OpenAI, Qwen, Groq, Moonshot, Doubao and ERNIE.

---

### 📚 More resources

- [GEO research paper](https://arxiv.org/abs/2311.09735) — Original GEO research
- [Project documentation](DOCS.md) — Complete feature documentation
- [Quick start](docs/guides/QUICK_START_GUIDE.md) — Getting started
''' + s[end:]
p.write_text(s, encoding='utf-8')

p = root/'modules/data_storage.py'
s = p.read_text(encoding='utf-8')
for method in ['get_articles', 'get_optimizations', 'get_verify_results', 'get_api_calls', 'get_workflow', 'list_workflows', 'get_workflow_template', 'get_workflow_templates', 'get_workflow_executions', 'get_publish_records', 'get_article_by_id']:
    s = s.replace('    def '+method+'(', '    @english_metadata\n    def '+method+'(')
p.write_text(s, encoding='utf-8')

# English matching is case-insensitive; weights and thresholds remain unchanged.
for filename in ['eeat_enhancer.py', 'fact_density_enhancer.py', 'content_scorer.py', 'negative_monitor.py']:
    p = root/'modules'/filename
    s = p.read_text(encoding='utf-8')
    tree = ast.parse(s)
    lines = s.splitlines(keepends=True)
    edits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 're' and node.func.attr in ('search', 'findall', 'finditer'):
            if len(node.args) == 2 and not node.keywords:
                offset = sum(len(line) for line in lines[:node.end_lineno-1]) + node.end_col_offset - 1
                # AST columns are UTF-8 bytes; convert to text positions on non-ASCII lines.
                prefix = lines[node.end_lineno-1].encode('utf-8')[:node.end_col_offset-1].decode('utf-8')
                offset = sum(map(len, lines[:node.end_lineno-1])) + len(prefix)
                edits.append(offset)
    for offset in sorted(edits, reverse=True):
        s = s[:offset] + ', flags=re.IGNORECASE' + s[offset:]
    # Existing MULTILINE calls also need case-insensitive English text matching.
    s = s.replace('content, re.MULTILINE)', 'content, re.MULTILINE | re.IGNORECASE)')
    s = s.replace('text, re.MULTILINE)', 'text, re.MULTILINE | re.IGNORECASE)')
    compile(s, filename, 'exec')
    p.write_text(s, encoding='utf-8')

# Keep dictionary matches consistent with lowercased input.
p = root/'modules/knowledge_base.py'
s = p.read_text(encoding='utf-8').replace('if pattern in sentence.lower():', 'if pattern.lower() in sentence.lower():')
s = s.replace('"Report" in text and ("《" in text or "year" in text)', '"report" in text.lower() and ("《" in text or any(c.isdigit() for c in text))')
s = s.replace('"Data" in text and any(c.isdigit() for c in text)', '"data" in text.lower() and any(c.isdigit() for c in text)')
p.write_text(s, encoding='utf-8')
p = root/'modules/keyword_data_enhancer.py'
s = p.read_text(encoding='utf-8').replace('if any(pattern in keyword for pattern in patterns):', 'if any(pattern.lower() in keyword.lower() for pattern in patterns):')
p.write_text(s, encoding='utf-8')
