"""
Analyze extracted papers from Computer Networks journal to find the most relevant baselines for FedSemGNN comparison.

This script:
1. Extracts text from all PDFs in extractedpapers folder
2. Identifies key topics and keywords
3. Ranks papers by relevance to FedSemGNN
4. Generates a summary report with recommendations
"""

import os
import re
from pathlib import Path
try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'PyPDF2'])
    import PyPDF2

# Define relevance scoring criteria
KEYWORDS = {
    'primary': {
        'federated learning': 5,
        'federated reinforcement learning': 8,
        'graph neural network': 7,
        'GNN': 7,
        'semantic': 6,
        'task placement': 8,
        'service placement': 7,
        'edge computing': 5,
        'edge orchestration': 6,
    },
    'secondary': {
        'reinforcement learning': 4,
        'deep reinforcement learning': 5,
        'PPO': 6,
        'policy gradient': 4,
        'multi-agent': 4,
        'hierarchical': 3,
        'resource allocation': 3,
        'offloading': 3,
        'latency': 2,
        'energy efficiency': 2,
        'power consumption': 2,
    },
    'methodology': {
        'simulation': 2,
        'EdgeSim': 4,
        'PyTorch': 3,
        'benchmark': 2,
        'evaluation': 1,
        'comparison': 1,
    }
}

NEGATIVE_KEYWORDS = {
    'blockchain': -2,
    'IoT security': -1,
    'attack': -1,
    'intrusion detection': -2,
    'privacy preservation': -1,
}


def extract_text_from_pdf(pdf_path, max_pages=10):
    """Extract text from first few pages of PDF (title, abstract, intro)."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            # Read first max_pages pages (usually contains title, abstract, intro)
            for i in range(min(max_pages, len(reader.pages))):
                page = reader.pages[i]
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading {pdf_path.name}: {e}")
        return ""


def extract_title(text):
    """Extract paper title from text."""
    # Look for common title patterns
    lines = text.split('\n')
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        line = line.strip()
        # Title is usually one of the first substantial lines
        if len(line) > 20 and len(line) < 200 and not line.startswith('http'):
            # Skip common header text
            if 'computer networks' in line.lower():
                continue
            if 'elsevier' in line.lower():
                continue
            if re.match(r'^\d+$', line):  # Skip page numbers
                continue
            if '@' in line or 'email' in line.lower():  # Skip emails
                continue
            return line
    
    # Fallback: return first substantial line
    for line in lines[:30]:
        line = line.strip()
        if len(line) > 30:
            return line[:150]  # Truncate long lines
    
    return "Title not found"


def calculate_relevance_score(text):
    """Calculate relevance score based on keyword matching."""
    text_lower = text.lower()
    score = 0
    matched_keywords = []
    
    # Primary keywords
    for keyword, value in KEYWORDS['primary'].items():
        if keyword.lower() in text_lower:
            score += value
            matched_keywords.append(f"{keyword} (+{value})")
    
    # Secondary keywords
    for keyword, value in KEYWORDS['secondary'].items():
        if keyword.lower() in text_lower:
            score += value
            matched_keywords.append(f"{keyword} (+{value})")
    
    # Methodology keywords
    for keyword, value in KEYWORDS['methodology'].items():
        if keyword.lower() in text_lower:
            score += value
            matched_keywords.append(f"{keyword} (+{value})")
    
    # Negative keywords (topics we want to avoid)
    for keyword, value in NEGATIVE_KEYWORDS.items():
        if keyword.lower() in text_lower:
            score += value
            matched_keywords.append(f"{keyword} ({value})")
    
    return score, matched_keywords


def extract_year(text):
    """Extract publication year from text."""
    # Look for patterns like "2023", "2024", "2025"
    years = re.findall(r'\b(202[0-5])\b', text[:1000])  # Check first 1000 chars
    if years:
        return years[0]  # Return first found year
    return "Unknown"


def check_has_experiments(text):
    """Check if paper has experimental evaluation."""
    text_lower = text.lower()
    experiment_indicators = [
        'evaluation', 'experiment', 'simulation', 'results',
        'performance', 'benchmark', 'comparison', 'dataset'
    ]
    return any(indicator in text_lower for indicator in experiment_indicators)


def extract_metrics(text):
    """Identify what metrics the paper reports."""
    text_lower = text.lower()
    metrics = []
    
    metric_keywords = {
        'latency': ['latency', 'delay', 'response time'],
        'energy/power': ['energy', 'power', 'consumption', 'battery'],
        'communication': ['communication', 'bandwidth', 'traffic', 'data transfer'],
        'accuracy': ['accuracy', 'precision', 'f1-score', 'success rate'],
        'throughput': ['throughput', 'requests per second', 'qps'],
        'cost': ['cost', 'overhead', 'resource utilization'],
        'convergence': ['convergence', 'training time', 'iterations'],
    }
    
    for metric_name, keywords in metric_keywords.items():
        if any(kw in text_lower for kw in keywords):
            metrics.append(metric_name)
    
    return metrics


def analyze_papers(folder_path):
    """Analyze all PDFs in the folder."""
    folder = Path(folder_path)
    pdf_files = list(folder.glob('*.pdf'))
    
    print(f"\n{'='*80}")
    print(f"Analyzing {len(pdf_files)} papers from Computer Networks journal...")
    print(f"{'='*80}\n")
    
    results = []
    
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}...")
        text = extract_text_from_pdf(pdf_file)
        
        if not text:
            continue
        
        title = extract_title(text)
        year = extract_year(text)
        score, keywords = calculate_relevance_score(text)
        has_experiments = check_has_experiments(text)
        metrics = extract_metrics(text)
        
        results.append({
            'filename': pdf_file.name,
            'title': title,
            'year': year,
            'score': score,
            'keywords': keywords,
            'has_experiments': has_experiments,
            'metrics': metrics,
        })
    
    # Sort by relevance score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results


def generate_report(results):
    """Generate a detailed report of the analysis."""
    report = []
    
    report.append("\n" + "="*80)
    report.append("BASELINE PAPER ANALYSIS REPORT")
    report.append("="*80 + "\n")
    
    # Top recommendations
    report.append("\n🏆 TOP 5 RECOMMENDED PAPERS FOR COMPARISON:\n")
    report.append("-" * 80)
    
    for i, paper in enumerate(results[:5], 1):
        report.append(f"\n{i}. SCORE: {paper['score']} | YEAR: {paper['year']}")
        report.append(f"   TITLE: {paper['title']}")
        report.append(f"   FILE: {paper['filename']}")
        if paper['metrics']:
            report.append(f"   METRICS: {', '.join(paper['metrics'])}")
        report.append(f"   HAS EXPERIMENTS: {'✓' if paper['has_experiments'] else '✗'}")
        if paper['keywords']:
            report.append(f"   MATCHED KEYWORDS: {', '.join(paper['keywords'][:5])}")
        report.append("")
    
    # Full ranking
    report.append("\n" + "="*80)
    report.append("COMPLETE RANKING (All Papers)")
    report.append("="*80 + "\n")
    
    for i, paper in enumerate(results, 1):
        report.append(f"{i:2d}. Score: {paper['score']:3d} | {paper['year']} | {paper['title'][:70]}")
    
    # Statistics
    report.append("\n" + "="*80)
    report.append("STATISTICS")
    report.append("="*80 + "\n")
    
    total = len(results)
    with_experiments = sum(1 for p in results if p['has_experiments'])
    recent = sum(1 for p in results if p['year'] in ['2023', '2024', '2025'])
    
    report.append(f"Total papers analyzed: {total}")
    report.append(f"Papers with experimental evaluation: {with_experiments} ({with_experiments/total*100:.1f}%)")
    report.append(f"Recent papers (2023-2025): {recent} ({recent/total*100:.1f}%)")
    report.append(f"Average relevance score: {sum(p['score'] for p in results)/total:.1f}")
    
    # Metric coverage
    report.append("\n📊 METRIC COVERAGE:")
    all_metrics = {}
    for paper in results:
        for metric in paper['metrics']:
            all_metrics[metric] = all_metrics.get(metric, 0) + 1
    
    for metric, count in sorted(all_metrics.items(), key=lambda x: x[1], reverse=True):
        report.append(f"   {metric}: {count} papers ({count/total*100:.1f}%)")
    
    # Recommendations
    report.append("\n" + "="*80)
    report.append("💡 RECOMMENDATIONS")
    report.append("="*80 + "\n")
    
    report.append("Based on the analysis, I recommend:")
    report.append("")
    report.append("1. START WITH TOP 3 PAPERS:")
    for i, paper in enumerate(results[:3], 1):
        report.append(f"   Paper {i}: {paper['title'][:70]}")
        report.append(f"            Relevance score: {paper['score']} | Year: {paper['year']}")
    
    report.append("\n2. IF YOU NEED MORE BASELINES, ADD:")
    for i, paper in enumerate(results[3:5], 4):
        report.append(f"   Paper {i}: {paper['title'][:70]}")
        report.append(f"            Relevance score: {paper['score']} | Year: {paper['year']}")
    
    report.append("\n3. NEXT STEPS:")
    report.append("   a. Read the top 3 papers' abstracts and evaluation sections")
    report.append("   b. Extract their experimental results (latency, power, etc.)")
    report.append("   c. Fill in PAPER_DATA_COLLECTION.md template")
    report.append("   d. I'll help you create comparison tables")
    
    report.append("\n4. EXPECTED OUTCOME:")
    report.append("   - 3-5 strong baseline comparisons")
    report.append("   - All from Computer Networks journal (2022-2025)")
    report.append("   - Cover similar metrics (latency, energy, communication)")
    report.append("   - Strengthen your evaluation section significantly")
    
    return "\n".join(report)


def save_detailed_analysis(results, output_file):
    """Save detailed analysis to markdown file."""
    md = []
    
    md.append("# Detailed Paper Analysis for FedSemGNN Baseline Comparison\n")
    md.append(f"*Analysis Date: October 18, 2025*\n")
    md.append(f"*Total Papers Analyzed: {len(results)}*\n")
    
    md.append("---\n")
    md.append("## 🎯 Selection Criteria\n")
    md.append("Papers are ranked based on relevance to FedSemGNN using keyword matching:\n")
    md.append("- **Primary keywords** (high weight): federated learning, GNN, semantic, task placement\n")
    md.append("- **Secondary keywords** (medium weight): RL, edge computing, resource allocation\n")
    md.append("- **Methodology keywords** (low weight): simulation, benchmark, evaluation\n")
    md.append("- **Negative keywords** (penalty): security-only, blockchain-only topics\n")
    
    md.append("\n---\n")
    md.append("## 📋 Top Papers (Ranked by Relevance)\n\n")
    
    for i, paper in enumerate(results, 1):
        md.append(f"### {i}. {paper['title']}\n")
        md.append(f"- **File:** `{paper['filename']}`\n")
        md.append(f"- **Year:** {paper['year']}\n")
        md.append(f"- **Relevance Score:** {paper['score']}\n")
        md.append(f"- **Has Experiments:** {'✓ Yes' if paper['has_experiments'] else '✗ No'}\n")
        
        if paper['metrics']:
            md.append(f"- **Metrics Reported:** {', '.join(paper['metrics'])}\n")
        
        if paper['keywords']:
            md.append(f"- **Matched Keywords:** {', '.join(paper['keywords'][:8])}\n")
        
        # Add recommendation badge
        if i <= 3:
            md.append(f"- **Recommendation:** 🏆 **HIGHLY RECOMMENDED** - Include in comparison\n")
        elif i <= 5:
            md.append(f"- **Recommendation:** ⭐ **RECOMMENDED** - Good alternative/addition\n")
        elif i <= 10:
            md.append(f"- **Recommendation:** 💡 Consider if needed\n")
        else:
            md.append(f"- **Recommendation:** Lower priority\n")
        
        md.append("\n")
    
    md.append("---\n")
    md.append("## 🎬 Next Actions\n\n")
    md.append("1. **Read top 3 papers** (highest relevance scores)\n")
    md.append("2. **Extract results** from their evaluation sections\n")
    md.append("3. **Fill data template** (PAPER_DATA_COLLECTION.md)\n")
    md.append("4. **Request help** to create comparison tables\n")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))


if __name__ == "__main__":
    # Analyze papers
    folder_path = "extractedpapers"
    results = analyze_papers(folder_path)
    
    # Generate and print report
    report = generate_report(results)
    print(report)
    
    # Save detailed analysis
    output_file = "PAPER_ANALYSIS_RESULTS.md"
    save_detailed_analysis(results, output_file)
    print(f"\n✅ Detailed analysis saved to: {output_file}")
    
    # Save top 5 for quick reference
    top5_file = "TOP_5_PAPERS.txt"
    with open(top5_file, 'w', encoding='utf-8') as f:
        f.write("TOP 5 RECOMMENDED PAPERS FOR FEDSEMGNN COMPARISON\n")
        f.write("="*80 + "\n\n")
        for i, paper in enumerate(results[:5], 1):
            f.write(f"{i}. {paper['title']}\n")
            f.write(f"   File: {paper['filename']}\n")
            f.write(f"   Year: {paper['year']} | Score: {paper['score']}\n")
            f.write(f"   Metrics: {', '.join(paper['metrics']) if paper['metrics'] else 'N/A'}\n")
            f.write("\n")
    
    print(f"✅ Top 5 summary saved to: {top5_file}")
    
    print("\n" + "="*80)
    print("🎉 ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nNext: Read {output_file} for detailed breakdown of all papers.")
    print("Then: Focus on extracting data from the top 3-5 recommended papers.")
