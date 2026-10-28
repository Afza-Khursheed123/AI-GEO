import io
import pathlib
import re
import tokenize

root = pathlib.Path(__file__).resolve().parents[1] / 'AIGEOTOOLS'
replacements = {
    'Discover GEO Related tools, Proxy, Papers and community resources, Expand the tool ecosystem': 'Explore GEO tools, AI services, research papers and community resources.',
    'AI Search engines and content generation services, Used for validation and optimization GEO Performance': 'AI search and content services for validating and improving GEO performance.',
    'GEO related tools and services, Help improve content performance': 'Tools and services for improving GEO content performance.',
    'GEO related papers, Guide, Document, Learn more GEO Strategy': 'Research papers, guides and documentation on GEO strategy.',
    'GEO related communities and forums, Share experiences with other users': 'Communities and forums for sharing GEO experience.',
    'Search resource names by keyword, Description, Features...': 'Search names, descriptions and features...',
    'AI Search engine, Available for validation GEO Performance': 'AI search engine for validating GEO performance',
    'OpenAI search feature, Validate brand presence in AI Search performance': 'OpenAI search service for checking brand visibility in AI answers',
    'Google Search Generative Experience, Learn about AI Search trends': 'Google Search Generative Experience for exploring AI search trends',
    'AI Content creation platform, Supported SEO Generate optimized content': 'AI content platform with SEO optimization support',
    'SEO Content optimization tools, Supported SERP Analysis': 'SEO content optimization with SERP analysis',
    'Monitor your website in Google Search performance': 'Monitor your website’s performance in Google Search',
    'Validation JSON-LD Schema Is the markup correct?': 'Validate JSON-LD Schema markup',
    'Test whether the page supports Google Rich results': 'Test whether a page supports Google rich results',
    'Analyze web performance, Core Web Vitals Metrics': 'Analyze web performance and Core Web Vitals',
    'Optimize an existing article, Generate structured data and technical configuration, Improve GEO Performance': 'Optimize articles and generate structured data and technical configuration for GEO.',
    'Paste or upload an existing article, Enhance GEO Performance (Structured, Citable, Integrate the brand naturally)': 'Paste or upload an article to improve its structure, citability and natural brand mentions.',
    'Optional, Increase GEO Performance. Techniques dynamically adjust the article optimization strategy. ': 'Optional techniques adjust the optimization strategy to improve GEO performance.',
    'Paste the article content above first, or upload TXT/MD File. ': 'Paste the article above or upload a TXT or Markdown file.',
    'No generation model is currently available, First, in【Global settings】Configure the model in/API Configuration. ': 'No generation model is available. Configure a model and API key in the sidebar first.',
    'Keep the length within this percentage of the original 1.0-1.3 times': 'Keep the article between 1.0 and 1.3 times its original length',
    'At least 1 statements of experience': 'Include at least one statement of experience',
    'Evaluate and improve content expertise, Experience, Authority, Trustworthiness': 'Evaluate and improve expertise, experience, authoritativeness and trustworthiness.',
    'Enhancement will replace the current optimized result, Download a backup first. ': 'Enhancement replaces the current optimized article. Download a backup first.',
    'Generate content following Schema.org standard JSON-LD Code, Improve the brand\'s presence in AI entity recognition and authority in models': 'Generate Schema.org JSON-LD markup to help AI models identify the brand and its authority.',
    'Choose what suits your brand Schema Type': 'Choose the Schema type that suits your brand',
    'Enter the brand name and strengths in Basic Information first, Regenerate Schema. ': 'Enter the brand name and strengths in Basic Information, then generate the Schema markup.',
    '💡 **Instructions**: Apply HTML Script Copy the tags to your website `<head>` Some, or JSON-LD Add the code to GitHub README Medium. ': '💡 **Instructions**: Copy the HTML script tags into your website’s `<head>`, or include the JSON-LD in your GitHub README.',
    'Generate robots.txt, sitemap.xml and other technical configuration files, Improve content indexing (Improve 20-30%)': 'Generate robots.txt, sitemap.xml and other configuration files to improve content indexing (estimated improvement: 20–30%).',
    'Control search engine crawler access, Improve content indexing': 'Control crawler access to improve content indexing.',
    'Your website\'s basic URL': 'Website base URL',
    'Use the complete URL (including http/https), Avoid robots.txt contains invalid links. ': 'Use a complete URL, including http:// or https://, to avoid invalid links in robots.txt.',
    'Use the complete URL (including http/https), Avoid sitemap.xml contains invalid links. ': 'Use a complete URL, including http:// or https://, to avoid invalid links in sitemap.xml.',
    '💡 **Instructions**: Apply robots.txt Upload the file to your website\'s root directory': '💡 **Instructions**: Upload robots.txt to your website’s root directory',
    'Help search engines discover and index all your pages, Improve content indexing': 'Help search engines discover and index your pages.',
    '💡 **Instructions**: Apply sitemap.xml Upload the file to your website\'s root directory (for example https://example.com/sitemap.xml), and in Google Search Console Submit in': '💡 **Instructions**: Upload sitemap.xml to your website’s root directory (for example, https://example.com/sitemap.xml), then submit it in Google Search Console.',
    'Automated monitoring GEO Performance, Use data to optimize content strategy': 'Monitor GEO performance and use data to improve your content strategy.',
    'Automatically validate historical keywords across models, Generate data reports': 'Validate saved keywords across models and generate reports.',
    '💡 Tip: First, in【1 Keyword research】Generate keywords, before running automatic validation. ': '💡 Generate keywords in the “Keyword research” tab before running automatic validation.',
    'Configure at least one validation model in the sidebar LLM. ': 'Configure at least one validation model in the sidebar.',
    'Selection criteria 5 items': 'List five selection criteria',
    'Maximum recommended options 3 items (Mention the brand only if it meets the criteria)': 'Recommend up to three options. Mention the brand only if it meets the criteria.',
    '4 items FAQ': 'Answer four frequently asked questions',
    'Quantify GEO Return on investment, Optimize costs, Data-driven decisions': 'Measure GEO return on investment and identify cost improvements.',
    '📊 None yet API Call history. After you start using the tool, Cost data is recorded automatically. ': '📊 No API calls recorded yet. Cost data is collected automatically as you use the tool.',
    'Analyze content trustworthiness, Authority, engagement and other key metrics, Quantify content quality': 'Measure content trustworthiness, authority, engagement and overall quality.',
    'Each 100 Trust signals (Source placeholders, Data, case studies, etc.)': 'Trust signals per 100 characters (source placeholders, data, case studies, etc.)',
    '💡 Tip: First, in【2 Content creation】Generate content, before viewing content quality metrics. ': '💡 Generate articles in “Content creation” before viewing content quality metrics.',
    'Analyze brand mentions in negative queries, Provide risk alerts and optimization recommendations': 'Analyze brand mentions in negative queries, identify risks and suggest improvements.',
    '💡 Tip: No negative mention monitoring data. Please use【4 Multi-model validation】Enable negative mention monitoring, Generate and validate negative queries. ': '💡 No negative mention data yet. Enable monitoring in “Multi-model validation”, then generate and validate negative queries.',
    'Based on existing keywords, Expand related keywords through semantic similarity, Expand keyword coverage': 'Expand keyword coverage with semantically related queries.',
    'Generate 20 new GEO Optimize keywords': 'Generate 20 new GEO keywords',
    'No keywords found': 'No keywords found',
    'GEO Accessibility assessment': 'GEO accessibility assessment',
    'AI generationd': 'AI-generated',
    'Use LLM Evaluate in detail': 'Use an LLM for a detailed assessment',
    'What are the strengths of your product??': 'What are the strengths of your product?',
    'Q: What are the strengths of your product?': 'Q: What are the main strengths of your product?',
    'A: Our product has the following key strengths: 1)AI Enable deeper integration...; 2)Complete workflow coverage...; 3)Data-driven decisions...': 'A: It provides AI assistance, an end-to-end workflow and analytics for informed decisions.',
    'A: Just three steps: 1)Register an account; 2)Configure basic information; 3)Start using the core features. ': 'A: Create an account, configure your basic information, then start using the core features.',
    'Paste AI-generated content, Check whether the cited sources are genuine...': 'Paste AI-generated content to check its source citations...',
}
for p in [root/'geo_tool.py', *root.joinpath('modules').rglob('*.py'), *root.joinpath('platform_sync').rglob('*.py')]:
    tokens = []
    for token in tokenize.generate_tokens(io.StringIO(p.read_text(encoding='utf-8')).readline):
        if token.type in (tokenize.STRING, tokenize.FSTRING_MIDDLE) and not re.match(r'(?i)[ubf]*r', token.string):
            value = token.string
            for old, new in replacements.items():
                value = value.replace(old, new)
            token = token._replace(string=value)
        tokens.append(token)
    s = tokenize.untokenize(tokens)
    if p.name == 'fact_density_enhancer.py':
        s = s.replace('You are ', 'Write all prose in English. Preserve technical identifiers and JSON field names.\nYou are ')
        s = s.replace('re.search(p, content)', 're.search(p, content, re.IGNORECASE)')
        s = s.replace('content, re.MULTILINE)', 'content, re.MULTILINE | re.IGNORECASE)')
        s = s.replace('content[:200]))', 'content[:200], re.IGNORECASE))').replace('content[-200:]))', 'content[-200:], re.IGNORECASE))')
    compile(s, str(p), 'exec')
    p.write_text(s, encoding='utf-8')
