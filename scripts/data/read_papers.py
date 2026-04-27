import PyPDF2

papers = [
    '1-s2.0-S1389128623003791-main.pdf',
    '1-s2.0-S1389128623002529-main.pdf',
    '1-s2.0-S1389128624002330-main.pdf'
]

for i, p in enumerate(papers, 3):
    path = f'extractedpapers/{p}'
    with open(path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = reader.pages[0].extract_text()[:1500]
        print(f"\n{i}. {p}")
        print(text)
        print("="*80)
