import ast
import io
import pathlib
import re
import subprocess
import tokenize

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
mapping = dict(line.split('\t', 1) for line in pathlib.Path(__file__).with_name('translations.tsv').read_text(encoding='utf-8').splitlines() if '\t' in line)
han = re.compile(r'[\u3400-\u9fff]+')

# Keep the original matchers as alternatives so existing Chinese content remains supported.
for p in [ROOT/'geo_tool.py', *ROOT.joinpath('modules').rglob('*.py'), *ROOT.joinpath('platform_sync').rglob('*.py')]:
    original = subprocess.run(['git', 'show', 'HEAD:'+p.relative_to(ROOT).as_posix()], cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
    originals = {t.start: t.string for t in tokenize.generate_tokens(io.StringIO(original).readline) if t.type == tokenize.STRING and re.match(r'(?i)[ubf]*r', t.string) and han.search(t.string)}
    source = p.read_text(encoding='utf-8')
    tokens = []
    for t in tokenize.generate_tokens(io.StringIO(source).readline):
        if t.start in originals:
            raw = originals[t.start]
            def sub(m):
                before = raw[:m.start()]
                # Unicode ranges and Chinese numeral character classes are compatibility syntax.
                if before.rfind('[') > before.rfind(']'):
                    return m[0]
                translated = mapping.get(m[0], m[0])
                if translated == m[0]:
                    return m[0]
                translated = {'问题': 'problems?|issues?', '显示': 'shows?', '表明': 'indicates?', '报告': 'reports?', '研究': 'research|studies', '数据': 'data', '步骤': 'steps?', '第': 'step\\s*', '总结': 'summary|summarize', '结论': 'conclusions?'}.get(m[0], translated)
                translated = translated.replace(' ', r'\s+').replace("'", r"\'")
                return '(?:' + m[0] + '|\\s*' + translated + r'\s*' + ')'
            t = t._replace(string=han.sub(sub, raw))
        tokens.append(t)
    source = tokenize.untokenize(tokens)
    compile(source, str(p), 'exec')
    p.write_text(source, encoding='utf-8')

replacements = {
    'AI Generate': 'AI generation',
    'Generate&Optimization': 'Generation and optimization',
    'Generate&for optimization': 'for generation and optimization',
    'Generate&': 'Generation and ',
    'AI Powered brand content strategy · Help your brand stand out in AI Stand out in AI conversations': 'AI-powered brand content strategy · Stand out in AI conversations',
    'Records API Cost recording failed': 'Could not record API cost',
    'API Keys Configure in `.streamlit/secrets.toml` Configure manually in the file. ': 'Configure API keys manually in `.streamlit/secrets.toml`.',
    'Cannot save configuration locally config.json, The changes are active for this session. Check file permissions. ': 'Could not save config.json. The changes are active for this session. Check file permissions.',
    'Generation and optimization LLM of API Key Not entered': 'Enter an API key for the generation and optimization model',
    'of API Key Not entered': 'API key is missing',
    'Key strengths/Selling points (AI Dedicated)': 'Key strengths / selling points for AI content',
    'Generation temperature (More consistent→Lower)': 'Generation temperature (lower values are more consistent)',
    'All features are available, Ready to use': 'All features are ready to use',
    'Workflow cycle: Keyword → Create content → Optimization → Validation': 'Workflow: Keywords → Create → Optimize → Validate',
    'Complete edition: GitHub Template + Real multi-model validation + Existing article optimization + RAG Knowledge base • GEO Complete cycle, Focus on AI Brand influence': 'GitHub templates + Multi-model validation + Article optimization + RAG knowledge base • A complete GEO workflow for brand visibility in AI answers',
    'AI generation: Use LLM Generate directly; Keyword builder: Combine word bank terms; Hybrid mode: Combine terms, then refine the wording': 'AI generation: Generate queries with an LLM. Keyword builder: Combine word bank terms. Hybrid mode: Build keywords, then refine them with an LLM.',
    "All word bank types are shown side by side, Edit directly, Click each column's“Update”button or use the following“Update all word banks”button to save changes": 'Edit the word banks side by side. Save each column with “Update”, or use “Update all word banks” below.',
    'Word banks updated, Regenerate keywords to use the updated word banks': 'Word banks updated. Regenerate keywords to apply the changes.',
    'You are GEO (Generative Engine Optimization)Expert': 'You are a GEO (Generative Engine Optimization) expert',
    'You are GEO Expert +': 'You are a GEO expert and a',
    'You are an AI Search assistant, Like Baidu/WeChat Search AI Summary': 'You are an AI search assistant',
    'You are anAISearch assistant': 'You are an AI search assistant',
    'AI generation model': 'AI model',
    'Follow the following exactly JSON Return an array': 'Return a JSON array in the following format',
    'Follow the following exactly JSON output format': 'Follow this JSON output format exactly',
    'Use JSON Return an array': 'Return a JSON array',
    'Begin output JSON Array': 'Return the JSON array',
    'Approximately 30%Include brand keywords': 'Include the brand in approximately 30% of queries',
    'Approximately 70%generic keywords': 'Use generic keywords for approximately 70% of queries',
    'Call AI Generate keywords using a model': 'Generating keywords with the AI model',
    'Call AI generation keywords using a model': 'Generating keywords with the AI model',
    '**Possible causes: **': '**Possible causes:**',
    '**Suggested solutions: **': '**Suggested solutions:**',
    '**Instructions: **': '**Instructions:**',
    'API Key Invalid configuration or insufficient credit': 'Invalid API key or insufficient credit',
    "Check the sidebar's API Key Configuration": 'Check the API key configuration in the sidebar',
    'Confirm API Key valid and has sufficient credit': 'Confirm that the API key is valid and has sufficient credit',
    'Check API Is the service working?': 'Check that the API service is working',
    'Hybrid mode requires LLM Refine the wording': 'Hybrid mode requires an LLM to refine the wording',
    'in"Combination patterns"Region': 'In the “Combination patterns” section',
    'Click"': 'Click “',
    '"Word bank management"': '“Word bank management”',
    'Updated!Generated': 'Updated! Generated',
    'complete!Generated': 'complete! Generated',
    'complete!Added': 'complete! Added',
    'After completing configuration in the sidebar, Click“Generate keywords”. ': 'Complete configuration in the sidebar, then click “Generate keywords”.',
    'Analyze keywords in AI mention frequency and competition': 'Analyze keyword mention frequency and competition in AI answers',
    'Automatically generate keyword-based content following GEO professional content following these principles, Supports individual and batch generation': 'Generate professional content from keywords using GEO principles. Create one article or a batch.',
    'First, in【🎯 Keyword research】Generate keywords. ': 'Generate keywords in the “Keyword research” tab first.',
    'B Bilibili UP Main': 'Bilibili video creator',
    'B Bilibili': 'Bilibili',
    'Suitable for/and unsuitable audiences, each with 3 items': 'List three suitable and three unsuitable audiences',
    'Ending 8 search queries': 'End with eight relevant search queries',
    '3 items SEO Search-friendly title': '3 SEO-friendly titles',
    'Recommendations 3-5 images': 'Recommend 3-5 images',
    'At least 1 standard source placeholders': 'At least one standard source placeholder',
    'Directory+Sections+Summary': 'Table of contents + Sections + Summary',
    'Directory-Body (Chapters)-Summary': 'Table of contents - Body (Chapters) - Summary',
    'Standards README Structure': 'Standard README structure',
    'Aim for large language models to (especially code models)Preferential citation': 'Make the documentation easy for large language models, especially code models, to cite',
    'Prompt is empty': 'prompt is empty',
    'Image generation API Empty result returned': 'The image generation API returned an empty result',
    'API Key to enable image generation': 'API key to enable image generation',
    'Configure Wanx in the sidebar API key': 'Configure the Wanx API key in the sidebar',
    'Smart generation: AI Analyze content automatically to generate images; Based on the description: Use generated illustration briefs': 'Smart generation: Create images from the article. From description: Use existing illustration briefs.',
    'Analyze whether the brand name and strengths GEO Friendly, Provide optimization recommendations. Apply the optimized settings to the global configuration. ': 'Evaluate the brand name and value proposition for GEO, then apply the recommended settings to the global configuration.',
    "Complete the sidebar configuration and click'Apply configuration'": 'Complete the sidebar configuration and click “Apply configuration”.',
    'Automatically publish generated articles to platforms, Supported API Publishing and quick copy': 'Publish generated articles through supported APIs, or copy them for manual publishing.',
    'Configuration GitHub Account information, Used to publish articles automatically to GitHub Repository': 'Configure your GitHub account to publish articles automatically to a repository.',
    'in https://github.com/settings/tokens Create Token, Required repo Permissions': 'Create a token at https://github.com/settings/tokens with access to the target repository.',
    'GitHub Token Validation failed, Check Token Is it correct?': 'GitHub token validation failed. Check the token and repository permissions.',
    'Configure first GitHub Account': 'Configure a GitHub account first',
    'FAQ Some': 'FAQ section',
    'GEO Friendly': 'GEO-friendly',
    'GEOImprove accessibility': 'GEO accessibility improvement',
    'GEO Improve accessibility': 'GEO accessibility improvement',
    'For example"': 'For example, "',
    'for example"': 'for example, "',
    'Use"': 'Use "',
    '"and similar statements': '" and similar statements',
    '"and similar placeholders': '" and similar placeholders',
    'Markdown Complete output': 'Return the complete Markdown document',
    '5-12words': '5-12 words',
    '8-30 words': '5-15 words',
    '2025 year': 'this year',
    '2025 best this year': 'Best',
    'best{industry}What software options are available?': 'What are the best {industry} tools?',
    'best {industry} What software options are available?': 'What are the best {industry} tools?',
    '{brand} Tutorial': 'How do I get started with {brand}?',
    '"ERP Recommended" → "ERP Which is best?", "How to choose ERP"': '"ERP recommendations" → "Which ERP system is best?", "How do I choose an ERP system?"',
    '"for small businesses CRM software"': '"CRM software for small businesses"',
    'For each keyword include: category': 'For each keyword include: category',
    'GEO Optimize keywords': 'GEO keywords',
}
for p in [ROOT/'geo_tool.py', *ROOT.joinpath('modules').rglob('*.py'), *ROOT.joinpath('platform_sync').rglob('*.py')]:
    source = p.read_text(encoding='utf-8')
    # Apply editorial corrections only within string tokens, preserving comments and code.
    result = []
    for t in tokenize.generate_tokens(io.StringIO(source).readline):
        if t.type in (tokenize.STRING, tokenize.FSTRING_MIDDLE) and not re.match(r'(?i)[ubf]*r', t.string):
            value = t.string
            for old, new in replacements.items():
                value = value.replace(old, new)
            if 'You are ' in value and '\n' in value:
                value = value.replace('You are ', 'Write all prose in English. Preserve technical identifiers and JSON field names.\nYou are ', 1)
            t = t._replace(string=value)
        result.append(t)
    edited = tokenize.untokenize(result)
    compile(edited, str(p), 'exec')
    p.write_text(edited, encoding='utf-8')
