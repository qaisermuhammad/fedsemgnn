import re
import sys

with open('sections/main.tex', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

errors = []

# Check balanced braces
depth = 0
for i, line in enumerate(lines, 1):
    clean = re.sub(r'(?<!\\)%.*$', '', line)
    for c in clean:
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                errors.append(f'BRACE ERROR line {i}: Unmatched closing brace')
                depth = 0

if depth != 0:
    errors.append(f'BRACE ERROR: {depth} unclosed braces at end of file')
else:
    print('OK: All braces balanced')

# Check begin/end environment matching
env_stack = []
for i, line in enumerate(lines, 1):
    clean = re.sub(r'(?<!\\)%.*$', '', line)
    for m in re.finditer(r'\\begin\{(\w+)\}', clean):
        env_stack.append((m.group(1), i))
    for m in re.finditer(r'\\end\{(\w+)\}', clean):
        if env_stack and env_stack[-1][0] == m.group(1):
            env_stack.pop()
        elif env_stack:
            errors.append(f'ENV ERROR line {i}: \\end{{{m.group(1)}}} but expected \\end{{{env_stack[-1][0]}}} (opened line {env_stack[-1][1]})')
        else:
            errors.append(f'ENV ERROR line {i}: \\end{{{m.group(1)}}} with no matching \\begin')

for env, line in env_stack:
    errors.append(f'ENV ERROR: Unclosed \\begin{{{env}}} at line {line}')

if not any('ENV ERROR' in e for e in errors):
    print('OK: All environments balanced')

# Check for common issues
for i, line in enumerate(lines, 1):
    # Missing $ around math
    if '\\times' in line and '$' not in line and '\\[' not in line:
        errors.append(f'WARNING line {i}: \\times outside math mode? {line.strip()[:60]}')
    
    # Check for \\ at end of tabular rows (missing \\)
    # Check for common typos
    if '\\textbf{}' in line:
        errors.append(f'WARNING line {i}: Empty \\textbf{{}}')

if errors:
    print(f'\n{len(errors)} issues found:')
    for e in errors:
        print(f'  {e}')
else:
    print('OK: No issues found')

print(f'\nTotal lines: {len(lines)}')
