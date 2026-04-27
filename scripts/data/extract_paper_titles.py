"""
Extract actual paper titles from the top-ranked PDFs.
The first script extracted generic headers - this will get real titles.
"""

import PyPDF2
from pathlib import Path
import re


def extract_real_title(pdf_path):
    """Extract the actual paper title by reading more intelligently."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Read first 3 pages
            text = ""
            for i in range(min(3, len(reader.pages))):
                text += reader.pages[i].extract_text()
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Look for actual title (usually appears after journal name)
            found_journal = False
            title_candidates = []
            
            for i, line in enumerate(lines):
                # Skip common headers
                if any(skip in line.lower() for skip in ['computer networks', 'elsevier', 'contents lists', 
                                                          'sciencedirect', 'available online', 'journal homepage']):
                    found_journal = True
                    continue
                
                # Skip URLs, emails, page numbers
                if 'http' in line or '@' in line or re.match(r'^\d+$', line):
                    continue
                
                # Skip very short lines
                if len(line) < 20:
                    continue
                
                # Skip lines with only author names (often have commas or "and")
                if line.count(',') > 3:
                    continue
                
                # After finding journal info, next substantial line is likely title
                if found_journal and len(line) > 30 and len(line) < 300:
                    # Check if it looks like a title (capitalized, not all caps unless short)
                    if not line.isupper() or len(line) < 50:
                        title_candidates.append(line)
                        if len(title_candidates) >= 3:
                            break
            
            # Return the best candidate
            if title_candidates:
                # Prefer longer titles (more complete)
                return max(title_candidates, key=len)
            
            # Fallback: look for lines between 40-200 chars after first 5 lines
            for line in lines[5:30]:
                if 40 < len(line) < 200 and not any(skip in line.lower() for skip in 
                    ['available', 'received', 'revised', 'accepted', 'published', 'elsevier', 'all rights']):
                    return line
            
            return "Title extraction failed - manual review needed"
    
    except Exception as e:
        return f"Error: {e}"


def extract_authors(pdf_path):
    """Try to extract author names."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = reader.pages[0].extract_text()
            
            # Look for author patterns
            lines = text.split('\n')
            for i, line in enumerate(lines[:50]):
                # Authors often appear before abstract
                if 'abstract' in line.lower():
                    # Check previous lines
                    for j in range(max(0, i-10), i):
                        author_line = lines[j].strip()
                        if 10 < len(author_line) < 100 and ',' in author_line:
                            return author_line
                    break
            
            return "Authors not extracted"
    except:
        return "Error"


# Top 5 papers to analyze
top_papers = [
    "1-s2.0-S1389128625000301-main.pdf",
    "1-s2.0-S1389128624006868-main.pdf", 
    "1-s2.0-S1389128623003791-main.pdf",
    "1-s2.0-S1389128623002529-main.pdf",
    "1-s2.0-S1389128624002330-main.pdf",
]

print("\n" + "="*80)
print("EXTRACTING ACTUAL TITLES FROM TOP 5 PAPERS")
print("="*80 + "\n")

results = []
for i, filename in enumerate(top_papers, 1):
    pdf_path = Path("extractedpapers") / filename
    if pdf_path.exists():
        print(f"{i}. Processing: {filename}")
        title = extract_real_title(pdf_path)
        authors = extract_authors(pdf_path)
        
        print(f"   Title: {title}")
        print(f"   Authors: {authors}")
        print()
        
        results.append({
            'rank': i,
            'filename': filename,
            'title': title,
            'authors': authors
        })

# Save results
with open("TOP_5_PAPERS_WITH_TITLES.md", 'w', encoding='utf-8') as f:
    f.write("# Top 5 Papers for FedSemGNN Baseline Comparison\n\n")
    f.write("*Extracted from Computer Networks journal PDFs*\n\n")
    f.write("---\n\n")
    
    for paper in results:
        f.write(f"## {paper['rank']}. {paper['title']}\n\n")
        f.write(f"- **File:** `{paper['filename']}`\n")
        f.write(f"- **Authors:** {paper['authors']}\n")
        f.write(f"- **Status:** 🏆 Highly recommended for comparison\n\n")
        f.write("**Next Steps:**\n")
        f.write("1. Read abstract and evaluation sections\n")
        f.write("2. Extract performance metrics (latency, power, accuracy, etc.)\n")
        f.write("3. Note experimental setup details\n")
        f.write("4. Fill in PAPER_DATA_COLLECTION.md\n\n")
        f.write("---\n\n")

print("✅ Results saved to: TOP_5_PAPERS_WITH_TITLES.md")
