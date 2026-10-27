import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser
from quarterly import entries, build, render_article, render_index

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.hrefs.extend(v for k,v in attrs if k == 'href')

class QuarterlyTests(unittest.TestCase):
    def test_every_archive_and_neighbor_link_has_a_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            pages=list(Path(tmp).rglob('*.html'))
            self.assertEqual(len(pages),len(entries())+1)
            for page in pages:
                parser=Links();parser.feed(page.read_text())
                for href in parser.hrefs:
                    path=href.split('#')[0]
                    if path.startswith('/quarterly'):
                        self.assertTrue((Path(tmp)/path.lstrip('/')/'index.html').is_file(),href)

    def test_unknown_articles_do_not_resolve(self):
        self.assertIsNone(render_article('does-not-exist'))
        self.assertIsNone(render_article('../operator'))

    def test_source_sensitive_details_absent_from_public_prose(self):
        text='\n'.join(e['body'] for e in entries())
        for term in ('@army.mil','@mail.smil.mil','CS8797979','CS8776501','SIPR','OPORD','Fight Tonight','Taunusstraße 22'):
            self.assertNotIn(term,text)

    def test_rendered_journal_omits_author_identity_and_unit_names(self):
        import re
        pages = [render_index()] + [render_article(e['slug']) for e in entries()]
        forbidden = r'\b(?:Samuel|Sam|Holliday|COIC|7ATC|7th Army Training Command|SOUTHCOM|EUCOM|209th|USAREUR(?:-AF)?)\b'
        for page in pages:
            self.assertIsNone(re.search(forbidden, page, re.IGNORECASE))

    def test_render_is_csp_compatible_and_complete(self):
        for page in [render_index()]+[render_article(e['slug']) for e in entries()]:
            self.assertNotIn('%%',page)
            self.assertNotIn('onclick=',page)
            self.assertNotIn('onsubmit=',page)
            self.assertIn('<h1>',page)
            self.assertIn('rel="canonical"',page)

if __name__=='__main__': unittest.main()
