"""
Generate a marked-up LaTeX file highlighting revisions.

Strategy:
- For paragraph text: wrap in \\textcolor{revblue}{...}
- For table rows (containing &): DON'T color (too fragile)
- For the abstract: use \\color{revblue} without braces
- For structural commands: skip
"""

import difflib
import re

OLD_TEX = r"D:\FedSemGNN\Paper Latex\FedSemGNN\main.tex"
NEW_TEX = r"D:\FedSemGNN\sections\main.tex"
OUT_TEX = r"D:\FedSemGNN\REVIEW\main_marked.tex"

with open(OLD_TEX, 'r', encoding='utf-8') as f:
    old_lines = f.readlines()
with open(NEW_TEX, 'r', encoding='utf-8') as f:
    new_lines = f.readlines()

# Stripped for comparison
old_stripped = [l.strip() for l in old_lines]
new_stripped = [l.strip() for l in new_lines]

sm = difflib.SequenceMatcher(None, old_stripped, new_stripped, autojunk=False)
opcodes = sm.get_opcodes()

changed_new_indices = set()
for tag, i1, i2, j1, j2 in opcodes:
    if tag in ('replace', 'insert'):
        for j in range(j1, j2):
            changed_new_indices.add(j)

print(f"Total new lines: {len(new_lines)}")
print(f"Changed/inserted lines: {len(changed_new_indices)}")

def should_not_color(line):
    """Lines that must NOT be wrapped in color groups."""
    s = line.strip()
    if not s:
        return True
    
    # Table rows (contain & and \\)
    if '&' in s and ('\\\\' in s or s.endswith('\\\\')):
        return True
    
    # Environment boundaries
    if s.startswith('\\begin{') or s.startswith('\\end{'):
        return True
    
    # Section commands
    if re.match(r'\\(section|subsection|subsubsection|label)\b', s):
        return True
    
    # Preamble / structural
    structural = [
        '\\documentclass', '\\usepackage', '\\renewcommand', '\\pgfplotsset',
        '\\usetikzlibrary', '\\title{', '\\author{', '\\maketitle',
        '\\bibliographystyle', '\\bibliography', '\\centering',
        '\\toprule', '\\midrule', '\\bottomrule', '\\hline',
        '\\definecolor', '\\graphicspath', '\\normalem',
        '\\small', '\\scriptsize', '\\normalsize',
    ]
    for cmd in structural:
        if s.startswith(cmd):
            return True
    
    # Author block lines
    if re.search(r'textsuperscript|\\\\.*\[.*pt\]|\\textit\{Emails|^\*Correspond', s):
        return True
    
    # Algorithmic lines
    if re.match(r'\\(STATE|IF|ENDIF|FOR|ENDFOR|RETURN|REQUIRE|ENSURE)\b', s):
        return True
    
    # Just closing braces
    if s == '}':
        return True
    
    # \multicolumn
    if '\\multicolumn' in s:
        return True
    
    # \footnotesize
    if s.startswith('\\footnotesize'):
        return True
    
    # \includegraphics (images don't take text color)
    if s.startswith('\\includegraphics'):
        return True
    
    return False


# Build output with context-aware coloring
output_lines = []
in_abstract = False
in_table = False
abstract_colored = False
preamble_done = False

for idx, line in enumerate(new_lines):
    stripped = line.strip()
    
    # Detect environments
    if stripped.startswith('\\begin{abstract}'):
        in_abstract = True
        abstract_colored = False
    elif stripped.startswith('\\end{abstract}'):
        if abstract_colored:
            indent = line[:len(line) - len(line.lstrip())]
            output_lines.append(f'{indent}\\color{{black}}\n')
        in_abstract = False
        output_lines.append(line)
        continue
    
    if stripped.startswith('\\begin{tabular'):
        in_table = True
    elif stripped.startswith('\\end{tabular'):
        in_table = False
    
    # Insert revision preamble after hyperref
    if not preamble_done and '\\usepackage' in stripped and 'hyperref' in stripped:
        output_lines.append(line)
        output_lines.append('\n')
        output_lines.append('% === REVISION MARKUP: Changed text shown in blue ===\n')
        output_lines.append('\\definecolor{revblue}{RGB}{0,0,180}\n')
        output_lines.append('\\graphicspath{{../figures/}}\n')
        output_lines.append('% === END REVISION MARKUP ===\n')
        output_lines.append('\n')
        preamble_done = True
        continue
    
    if idx not in changed_new_indices:
        # Unchanged line
        output_lines.append(line)
        continue
    
    # === Changed line ===
    
    # Inside abstract: use \color{revblue} without grouping
    if in_abstract:
        if not abstract_colored:
            indent = line[:len(line) - len(line.lstrip())]
            output_lines.append(f'{indent}\\color{{revblue}}\n')
            abstract_colored = True
        output_lines.append(line)
        continue
    
    # Inside table: don't color rows
    if in_table:
        output_lines.append(line)
        continue
    
    # Should not color this line type
    if should_not_color(line):
        output_lines.append(line)
        continue
    
    # === Safe to color ===
    indent = line[:len(line) - len(line.lstrip())]
    content = line.strip()
    
    # For \item lines: keep \item outside, color the rest
    if content.startswith('\\item'):
        # Extract \item (possibly with \textbf{...} prefix) and the rest
        item_match = re.match(r'(\\item\s*)', content)
        if item_match:
            item_prefix = item_match.group(1)
            rest = content[len(item_prefix):]
            output_lines.append(f'{indent}{item_prefix}\\textcolor{{revblue}}{{{rest}}}\n')
        else:
            output_lines.append(f'{indent}\\textcolor{{revblue}}{{{content}}}\n')
        continue
    
    # For \caption lines: DON'T color - it breaks \label resolution
    if content.startswith('\\caption'):
        output_lines.append(line)
        continue
    
    # For \noindent lines: wrap it all
    if content.startswith('\\noindent'):
        output_lines.append(f'{indent}\\textcolor{{revblue}}{{{content}}}\n')
        continue
    
    # For paragraph text: use \textcolor
    output_lines.append(f'{indent}\\textcolor{{revblue}}{{{content}}}\n')

# Write
with open(OUT_TEX, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

colored_count = sum(1 for l in output_lines if 'textcolor{revblue}' in l or ('\\color{revblue}' in l and 'definecolor' not in l))
print(f"Output: {len(output_lines)} lines ({colored_count} colored)")
print(f"Written to: {OUT_TEX}")
