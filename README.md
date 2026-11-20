# Documentation claim auditor

This offline static auditor compares documented claims about the checked capability with Python source patterns. It examines the root README and Markdown under docs, excluding fenced code; inline code counts. It reports unsupported affirmative claims and denials contradicted by production evidence. Tests are reported separately.

```sh
word-document-reading-claim-audit audit . --json --fail-on medium --ignore vendor/
python3 -m word_document_reading_claim_audit --version
```

Exit status 0 means PASS, 2 means a finding meets the threshold, and 1 indicates an input or usage error. The default threshold is high. Ignore prefixes may be repeated. Source is parsed, never executed; symlinks, examples, fixtures, and documentation are excluded from source evidence.

## Limitations

Exact phrases may describe opening an application, importing already processed data, a job title, or documentation abbreviated as “doc”. A file object may already have been opened elsewhere. External converters are deliberately not recognized. Static patterns count dead code, may miss alias chains, and require each route in one module. Denial handling depends on the listed phrases.

A call to the following constructor with an argument counts even if no content is subsequently accessed; without an argument it creates a blank file and does not count:

```python
from docx import Document
Document(path)
Document()
```

The following operations do not count: docx2txt argument parsing; mammoth images, transforms, and underline helpers; ODF loading, which covers several formats; pypandoc conversion or Python textract, which invoke external binaries; aspose.words (an unverified commercial SDK); docxtpl templates; Word COM automation; and subprocess invocations of LibreOffice, antiword, catdoc, or pandoc. Writing files alone does not count. Hand-written OOXML or ZIP parsing is also missed.

Text, HTML, Markdown, image, PDF, presentation, and spreadsheet access is outside the listed routes. Mindee, Azure Document Intelligence, Veryfi, Google Document AI, Eden AI, Textract, LlamaParse, Nanonets, Docsumo, ABBYY Vantage, Rossum, Klippa, Parseur, and Extend calls do not count: these are extraction services or use opaque identifiers rather than a listed operation.

Claims about spreadsheet and presentation access, PDF extraction, document generation, and other extraction families (including financial, identity, health, shipping, and business documents) are outside the phrase lists, as are document cropping, signatures, and payment processing.
