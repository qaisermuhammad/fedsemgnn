"""
Extract detailed information from paper: 1-s2.0-S1389128623004516-main.pdf
This paper uses Deep RL for edge computing offloading - very relevant!
"""

import PyPDF2
from pathlib import Path
import re

pdf_path = "extractedpapers/1-s2.0-S1389128623004516-main.pdf"

print("="*80)
print("ANALYZING: Deep RL-based Edge Computing Offloading")
print("="*80)

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    
    # Extract first 5 pages (intro + methodology)
    print("\n📄 EXTRACTING FIRST 5 PAGES...\n")
    text = ""
    for i in range(min(5, len(reader.pages))):
        text += reader.pages[i].extract_text()
    
    # Look for key sections
    print("TITLE:")
    print("Deep reinforcement learning-based edge computing offloading algorithm")
    print("for software-defined IoT")
    print()
    
    print("AUTHORS:")
    print("Xiaojuan Zhu, Tianhao Zhang, Jinwei Zhang, Bao Zhao, Shunxiang Zhang, Cai Wu")
    print("Affiliation: Anhui University of Science and Technology, China")
    print()
    
    print("YEAR: 2023")
    print()
    
    # Extract results sections (usually in later pages)
    print("\n📊 SEARCHING FOR RESULTS SECTIONS...\n")
    
    results_text = ""
    for i in range(len(reader.pages)):
        page_text = reader.pages[i].extract_text()
        
        # Look for results, evaluation, experimental sections
        if any(keyword in page_text.lower() for keyword in 
               ['result', 'experiment', 'evaluation', 'performance', 'comparison']):
            print(f"✓ Found relevant content on page {i+1}")
            results_text += f"\n--- PAGE {i+1} ---\n"
            results_text += page_text[:1500]  # First 1500 chars
    
    # Save extracted text
    with open("PAPER_ECO_SDIoT_EXTRACTED.txt", 'w', encoding='utf-8') as out:
        out.write("PAPER: Deep RL-based Edge Computing Offloading\n")
        out.write("="*80 + "\n\n")
        out.write("FULL TEXT (First 5 pages):\n")
        out.write(text[:5000])
        out.write("\n\n" + "="*80 + "\n")
        out.write("RESULTS SECTIONS:\n")
        out.write(results_text)
    
    print("\n✅ Extraction complete! Saved to: PAPER_ECO_SDIoT_EXTRACTED.txt")
    
    # Look for numerical results in text
    print("\n🔍 SEARCHING FOR METRICS...\n")
    
    # Look for common metric patterns
    metrics = {
        'latency': re.findall(r'latency[:\s]+(\d+\.?\d*)\s*(ms|s|seconds)', text.lower()),
        'delay': re.findall(r'delay[:\s]+(\d+\.?\d*)\s*(ms|s|seconds)', text.lower()),
        'energy': re.findall(r'energy[:\s]+(\d+\.?\d*)\s*(j|mj|w)', text.lower()),
        'cost': re.findall(r'cost[:\s]+(\d+\.?\d*)', text.lower()),
    }
    
    for metric, values in metrics.items():
        if values:
            print(f"✓ Found {metric}: {values[:3]}")  # Show first 3 matches

print("\n" + "="*80)
print("Next: Review PAPER_ECO_SDIoT_EXTRACTED.txt for detailed metrics")
print("="*80)
