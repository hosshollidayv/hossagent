"""Render the founder journal from edited, public-facing Markdown entries."""
from pathlib import Path
from html import escape
from datetime import date
import math
import re

ROOT = Path(__file__).resolve().parent
BASE = '/quarterly'

def entries():
    records = []
    for path in (ROOT / 'content' / 'quarterly').glob('*.md'):
        header, body = path.read_text(encoding='utf-8').split('\n\n', 1)
        record = dict(line.split(': ', 1) for line in header.splitlines())
        record.update(slug=path.stem, body=body.strip())
        record['minutes'] = max(1, math.ceil(len(body.split()) / 220))
        record['display_date'] = date.fromisoformat(record['Date']).strftime('%d %B %Y')
        records.append(record)
    return sorted(records, key=lambda e: (e['Date'], e['slug']), reverse=True)

def url(e):
    return f"{BASE}/{e['slug']}"

def frame(title, description, path, content, article=False):
    template = (ROOT / 'templates' / 'quarterly.html').read_text(encoding='utf-8')
    tokens = {'TITLE': escape(title), 'DESCRIPTION': escape(description, quote=True),
              'CANONICAL': 'https://hossagent.net' + path, 'CONTENT': content,
              'TYPE': 'article' if article else 'website'}
    for key, value in tokens.items():
        template = template.replace('%%' + key + '%%', value)
    return template

def meta(e):
    return f'<span>{escape(e["Category"])}</span><span>·</span><time datetime="{e["Date"]}">{e["display_date"]}</time><span>·</span><span>{e["minutes"]} min read</span>'

def render_index():
    all_entries = entries()
    featured = next(e for e in all_entries if e['slug'] == '27-guest-list')
    cards = []
    for i, e in enumerate(all_entries, 1):
        search = escape((e['Title'] + ' ' + e['Deck'] + ' ' + e['Category']).lower(), quote=True)
        cards.append(f'''<article class="entry" data-entry data-category="{escape(e['Category'], quote=True)}" data-search="{search}">
        <span class="entry-no" aria-hidden="true">{i:02d}</span><div><div class="meta">{meta(e)}</div>
        <h3><a href="{url(e)}">{escape(e['Title'])}</a></h3><p>{escape(e['Deck'])}</p></div>
        <a class="entry-arrow" href="{url(e)}" aria-label="Read {escape(e['Title'], quote=True)}">↗</a></article>''')
    categories = sorted(set(e['Category'] for e in all_entries))
    options = ''.join(f'<option>{escape(c)}</option>' for c in categories)
    body = f'''<section class="masthead"><div class="edition"><span>A HossAgent publication</span><span>Vol. 01 / Autumn 2026</span><span>Wiesbaden, Germany</span></div>
    <h1>Staff Officer’s<br><em>Quarterly.</em></h1><div class="masthead-bottom"><p>Field notes on people, systems,<br>and the work between them.</p><span class="seal" aria-label="Staff Officer’s Quarterly">SO<span>Q</span></span><p class="byline">The founder’s journal<br><strong>The Editor</strong></p></div></section>
    <section class="cover" aria-labelledby="cover-title"><div class="cover-label"><span class="eyebrow">The October issue</span><span class="large-number" aria-hidden="true">01</span><span class="small-label">The Christmas<br>Miracle Edition</span></div><div class="cover-copy"><div class="meta">{meta(featured)}</div><h2 id="cover-title"><a href="{url(featured)}">The Guest List</a></h2><p class="cover-deck">A sold-out show. A modest request.<br>Seven very good words.</p><p class="cover-excerpt">“You’re on the guestlist, merry Christmas.”<br>Alex Fang sent seven words. I have received considerably longer messages that accomplished less.</p><a class="read-link" href="{url(featured)}">Read the essay <span aria-hidden="true">↗</span></a></div></section>
    <section class="editor-note" aria-labelledby="editor-title"><p class="eyebrow">From the editor’s desk</p><div><h2 id="editor-title">Serious work.<br>A sense of proportion.</h2><p>I’m a product manager, staff officer, and founder of HossAgent. These are dispatches from a year in Germany—where a missing guitar, a parking lot, and a staff meeting can each tell you something about how the world works.</p><p>The Major’s Log supplies the material. The Quarterly gives it room to breathe.</p></div></section>
    <section class="archive" id="archive" aria-labelledby="archive-title"><div class="section-heading"><div><p class="eyebrow">The collected dispatches</p><h2 id="archive-title">October, in the field.</h2></div><span>{len(all_entries):02d} edited entries</span></div><form class="archive-tools" role="search" onsubmit="return false"><label>Find an entry<input id="journal-search" type="search" placeholder="Search titles and subjects" autocomplete="off"></label><label>Department<select id="journal-category"><option value="">All departments</option>{options}</select></label><button type="reset">Clear filters</button></form><p id="result-count" class="result-count" role="status" aria-live="polite">{len(all_entries)} entries</p><div>{''.join(cards)}</div><p id="no-results" hidden>No entries match. Try another phrase or clear the filters.</p></section>
    <section id="about" class="colophon"><p class="eyebrow">About the Quarterly</p><h2>Observed firsthand.<br>Reconsidered afterward.</h2><p>Personal essays adapted from the Major’s Log, correspondence, and conversations. Dates identify the source dispatch or reflection. Entries are edited for clarity, length, and a public audience; comic comparisons are the author’s own. This is an independent founder’s journal. Views are personal and do not represent any employer or institution.</p><a class="read-link" href="/hosstracker">Explore the work at HossAgent <span aria-hidden="true">↗</span></a></section>'''
    # CSP allows external scripts only. The form handler is attached in quarterly.js.
    body = body.replace(' onsubmit="return false"', '')
    return frame('Staff Officer’s Quarterly — HossAgent', 'The founder’s journal: field notes on people, systems, and the work between them. By The Editor.', BASE, body)

def render_article(slug):
    records = entries()
    index = next((i for i, e in enumerate(records) if e['slug'] == slug), None)
    if index is None:
        return None
    e = records[index]
    paragraphs = ''.join(f'<p>{escape(p.strip())}</p>' for p in re.split(r'\n\s*\n', e['body']) if p.strip())
    neighbors = []
    for label, other in [('Newer dispatch', index - 1), ('Earlier dispatch', index + 1)]:
        if 0 <= other < len(records):
            n = records[other]
            neighbors.append(f'<a href="{url(n)}"><span class="eyebrow">{label}</span><strong>{escape(n["Title"])}</strong><span aria-hidden="true">↗</span></a>')
    body = f'''<article class="reading"><header class="article-head"><a class="back-link" href="{BASE}#archive">← All dispatches</a><div class="meta">{meta(e)}</div><h1>{escape(e['Title'])}</h1><p class="article-deck">{escape(e['Deck'])}</p><div class="author-line"><span>By The Editor</span><button id="copy-link" type="button">Copy link</button><span id="copy-status" role="status" aria-live="polite"></span></div></header><div class="article-layout"><aside><span class="eyebrow">Major’s Log</span><span>October 2026</span><span>Wiesbaden<br>Germany</span><a href="{BASE}#about">About this journal ↗</a></aside><div class="prose">{paragraphs}<div class="end-mark" aria-label="End of essay">■</div><p class="editorial-caption">An edited personal reflection from the Major’s Log archive. Views are the author’s own.</p></div></div><nav class="article-neighbors" aria-label="More dispatches">{''.join(neighbors)}</nav></article>'''
    return frame(e['Title'] + ' — Staff Officer’s Quarterly', e['Deck'], url(e), body, True)

def build(destination):
    root = Path(destination) / 'quarterly'
    root.mkdir(parents=True, exist_ok=True)
    (root / 'index.html').write_text(render_index(), encoding='utf-8')
    for e in entries():
        folder = root / e['slug']
        folder.mkdir(exist_ok=True)
        (folder / 'index.html').write_text(render_article(e['slug']), encoding='utf-8')
