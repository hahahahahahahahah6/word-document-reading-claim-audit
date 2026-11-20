import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from word_document_reading_claim_audit.audit import audit, evidence
from word_document_reading_claim_audit.phrases import WORDDOCUMENTREADING, NOWORDDOCUMENTREADING, GENERIC_NAMES

YES = ('word document reading', 'read word document', 'reads word document', 'reading word document', 'read word documents', 'reads word documents', 'reading word documents', 'load word document', 'loads word document', 'loading word document', 'load word documents', 'loads word documents', 'loading word documents', 'open word document', 'opens word document', 'opening word document', 'open word documents', 'opens word documents', 'opening word documents', 'parse word document', 'parses word document', 'parsing word document', 'parse word documents', 'parses word documents', 'parsing word documents', 'import word document', 'imports word document', 'importing word document', 'import word documents', 'imports word documents', 'importing word documents', 'word document reader', 'word document parser', 'word document importer', 'word document loading', 'read docx', 'reads docx', 'reading docx', 'read docx file', 'reads docx file', 'load docx', 'loads docx', 'loading docx', 'open docx', 'opens docx', 'opening docx', 'read doc', 'reads doc', 'reading doc', 'load docx file')
NO = ('no word document reading', 'does not read word document', 'does not read word documents', 'does not support word document reading', 'without word document reading', 'no word document reader', 'does not load word document', 'does not load word documents', 'does not open word document', 'does not open word documents', 'does not parse word document', 'does not parse word documents', 'does not import word document', 'does not import word documents', 'no word document parser', 'does not read docx', 'does not read docx file', 'does not load docx', 'does not open docx', 'does not read doc', 'does not read doc file', 'does not load docx file', 'word document reading not supported', 'no word document reading support')
GENERIC = ('read_word_document', 'read_word_documents', 'load_word_document', 'load_word_documents', 'open_word_document', 'open_word_documents', 'parse_word_document', 'parse_word_documents', 'import_word_document', 'import_word_documents', 'read_docx', 'read_docx_file', 'load_docx', 'open_docx', 'read_doc', 'read_doc_file', 'load_docx_file', 'parse_docx', 'parse_doc', 'read_word', 'load_word', 'open_word', 'word_document_reader', 'read_docx_document')

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
    def write(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
    def cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'word_document_reading_claim_audit', *args], capture_output=True, text=True)
    def test_phrase_oracle(self):
        self.assertEqual(WORDDOCUMENTREADING, YES)
        self.assertEqual(NOWORDDOCUMENTREADING, NO)
        self.assertEqual(GENERIC_NAMES, GENERIC)
    def test_findings(self):
        self.write('README.md', 'read word document')
        self.assertEqual(audit(self.root)['findings'][0]['rule'], 'documented-word-document-reading-claim-false')
        self.assertEqual(self.cli('audit', str(self.root)).returncode, 2)
        self.write('tests/test_a.py', 'import docx\ndocx.Document("x")')
        self.assertEqual(audit(self.root)['findings'][0]['severity'], 'MEDIUM')
        self.assertEqual(self.cli('audit', str(self.root)).returncode, 0)
        self.assertEqual(self.cli('audit', str(self.root), '--fail-on', 'medium').returncode, 2)
        self.write('app.py', 'import docx\ndocx.Document("x")')
        self.assertEqual(audit(self.root)['verdict'], 'PASS')
        self.write('README.md', 'does not read word document')
        self.assertEqual(audit(self.root)['findings'][0]['rule'], 'documented-no-word-document-reading-claim-false')
        self.assertEqual(self.cli('audit', str(self.root)).returncode, 2)
        self.write('README.md', 'unrelated')
        self.assertEqual(audit(self.root)['verdict'], 'PASS')
    def test_docs(self):
        self.write('README.md', 'does not read word document')
        self.assertEqual(audit(self.root)['verdict'], 'PASS')
        self.write('README.md', '```\nread docx\n```')
        self.assertEqual(audit(self.root)['verdict'], 'PASS')
        self.write('README.md', '`read docx`')
        self.assertEqual(audit(self.root)['verdict'], 'FAIL')
        self.write('README.md', 'nothing')
        self.write('docs/a.md', 'read docx')
        self.assertEqual(audit(self.root, ['docs/'])['verdict'], 'PASS')
    def test_routes(self):
        cases = ['from docx import Document as D\nD("x")', 'import docx\ndocx.Document("x")', 'import docx as d\nd.Document("x")', 'from docx import Document\nDocument(docx="x")', 'from docx2txt import process as p\np("x")', 'import docx2txt as d\nd.process("x")']
        for n in ('convert_to_html', 'convert_to_markdown', 'extract_raw_text'):
            cases += ['from mammoth import '+n+' as f\nf("x")', 'import mammoth as m\nm.'+n+'("x")']
        cases += ['x.'+n+'()' for n in GENERIC] + ['from pkg import read_word_document as f\nf()']
        for source in cases:
            with self.subTest(source=source): self.assertTrue(evidence(source))
    def test_non_routes(self):
        cases = ['import '+n for n in ('docx','docx2txt','mammoth','odf','pypandoc','textract','aspose','docxtpl')]
        cases += ['import docx\ndocx.Document()', 'from docx import Document\nd=Document()\nd.add_paragraph("x")\nd.save("x")', 'import docx2txt\ndocx2txt.process_args()', 'import mammoth\nmammoth.images()', 'import mammoth\nmammoth.transforms()', 'from odf.opendocument import load\nload("x")', 'import pypandoc\npypandoc.convert_file("x")', 'import textract\ntextract.process("x")', 'import aspose.words\naspose.words.Document("x")', 'from docxtpl import DocxTemplate\nDocxTemplate("x")', 'import win32com.client\nwin32com.client.Dispatch("Word.Application")', 'import subprocess\nsubprocess.run(["antiword", "x"])', 'import subprocess\nsubprocess.run(["pandoc", "x"])', 'from pptx import Presentation\nPresentation("x")', 'from openpyxl import load_workbook\nload_workbook("x")', 'import pandas\npandas.read_excel("x")', 'import pypdf\npypdf.extract_text()', 'import pdfplumber\npdfplumber.extract_text()', 'open("x.txt").read()', 'from pathlib import Path\nPath("x").read_text()', 'from PIL import Image\nImage.open("x")', '"word document"', 'mindee.parse(InvoiceV4)', 'azure.begin_analyze_document("prebuilt-read")', 'veryfi.Client()', 'documentai.process_document()', 'textract.analyze_document()', 'eden.universal_ai()', 'llamaparse.parse()', 'nanonets.ocr(model_id="opaque")', 'docsumo.upload()', 'import docx\ndocx = object()\ndocx.Document("x")', 'from docx import Document\ndef Document(x): pass\nDocument("x")', 'def read_docx(): pass\nx.read_docx()', 'from docx import Document\nwith ctx() as Document: pass\nDocument("x")', 'from docx import Document\nDocument', 'from docx import Document\ninvalid !']
        for source in cases:
            with self.subTest(source=source): self.assertFalse(evidence(source))
    def test_exclusions_json(self):
        self.write('README.md', 'read docx')
        self.write('part.py', 'import docx')
        self.write('other.py', 'docx.Document("x")')
        self.write('examples/e.py', 'import docx\ndocx.Document("x")')
        self.write('fixtures/f.py', 'import docx\ndocx.Document("x")')
        (self.root / 'link.py').symlink_to(self.root / 'examples/e.py')
        result = json.loads(self.cli('audit', str(self.root), '--json').stdout)
        self.assertEqual(result['verdict'], 'FAIL')
        self.assertIn('message', result['findings'][0])
        self.assertEqual(self.cli('audit', str(self.root / 'missing')).returncode, 1)
        self.assertEqual(self.cli('bad').returncode, 1)
    def test_version(self):
        self.assertEqual(self.cli('--version').stdout.strip(), '0.1.0')

if __name__ == '__main__': unittest.main()
