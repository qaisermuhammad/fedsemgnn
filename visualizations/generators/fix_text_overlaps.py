#!/usr/bin/env python3
"""
Fix Text Overlapping Issues in All Individual Diagrams
This script applies systematic fixes to prevent text overlapping in all diagram files
"""

import os
import re

def fix_overlapping_text():
    """Apply fixes to all individual diagram files"""
    
    # Files to fix
    files_to_fix = [
        "fault_tolerance_metrics_individual.py",
        "semantic_learning_analysis_individual.py", 
        "temporal_performance_analysis_individual.py",
        "hardware_energy_modeling_individual.py"
    ]
    
    fixes_applied = []
    
    for filename in files_to_fix:
        if not os.path.exists(filename):
            print(f"⚠️  File not found: {filename}")
            continue
            
        print(f"🔧 Fixing text overlaps in {filename}...")
        
        # Read the file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply systematic fixes
        original_content = content
        
        # 1. Shorten method names to prevent x-axis label overlapping
        content = re.sub(r"'HSQF Heur\.'", "'HSQF'", content)
        content = re.sub(r"'RandomPlacement'", "'Random'", content)
        content = re.sub(r"'FedSemGNN\\n\(Ours\)'", "'FedSemGNN'", content)
        content = re.sub(r"'FedSemGNN \(Ours\)'", "'FedSemGNN'", content)
        
        # 2. Fix figure size and spacing
        content = re.sub(r"figsize=\(16, 12\)", "figsize=(18, 14)", content)
        content = re.sub(r"figsize=\(16, 8\)", "figsize=(18, 9)", content)
        
        # 3. Add subplot adjustments if missing
        if "fig.subplots_adjust" not in content:
            # Add after figsize line
            content = re.sub(
                r"(fig, .*plt\.subplots.*figsize=\([^)]+\)\))",
                r"\1\n    fig.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.12, wspace=0.25, hspace=0.35)",
                content
            )
        
        # 4. Reduce font sizes for legends and labels
        content = re.sub(r"fontsize=14,", "fontsize=12, pad=10,", content)
        content = re.sub(r"fontsize=16,", "fontsize=14,", content)
        content = re.sub(r"fontsize=10,", "fontsize=9,", content)
        content = re.sub(r"fontsize=11,", "fontsize=10,", content)
        
        # 5. Fix legend positioning and sizing
        content = re.sub(r"legend\(([^)]*)\)", lambda m: fix_legend(m.group(1)), content)
        
        # 6. Reduce bar width to prevent overlapping
        content = re.sub(r"width = 0\.25", "width = 0.18", content)
        content = re.sub(r"width = 0\.2(?!0)", "width = 0.15", content)
        
        # 7. Fix axis label rotations and sizes
        content = re.sub(r"rotation=15,", "rotation=25,", content)
        content = re.sub(r"rotation=20,", "rotation=30,", content)
        content = re.sub(r"ha='right'\)", "ha='right', fontsize=8)", content)
        
        # 8. Fix metric specification box positioning and size
        content = re.sub(
            r"fig\.text\(0\.02, 0\.98,",
            "fig.text(0.02, 0.95,",
            content
        )
        content = re.sub(
            r"fontsize=10,\s*verticalalignment='top'",
            "fontsize=8, verticalalignment='top'",
            content
        )
        
        # 9. Fix title positioning
        content = re.sub(r"y=0\.95\)", "y=0.98)", content)
        content = re.sub(r"y=0\.96\)", "y=0.98)", content)
        
        # 10. Fix tight_layout rect
        content = re.sub(
            r"plt\.tight_layout\(rect=\[[^\]]+\]\)",
            "plt.tight_layout(rect=[0, 0, 1, 0.87])",
            content
        )
        
        # Write back if changes were made
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            fixes_applied.append(filename)
            print(f"✅ Fixed {filename}")
        else:
            print(f"📝 No changes needed for {filename}")
    
    return fixes_applied

def fix_legend(legend_params):
    """Fix legend parameters to prevent overlapping"""
    # Add fontsize and better positioning if not present
    if "fontsize=" not in legend_params:
        legend_params += ", fontsize=8"
    if "ncol=" not in legend_params:
        legend_params += ", ncol=1"
    return f"legend({legend_params})"

def main():
    """Main function to apply all fixes"""
    print("🔧 FedSemGNN Text Overlap Fix Tool")
    print("=" * 50)
    
    fixed_files = fix_overlapping_text()
    
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Files fixed: {len(fixed_files)}")
    
    if fixed_files:
        print(f"\n🔧 Fixed files:")
        for f in fixed_files:
            print(f"   • {f}")
        
        print(f"\n🚀 Regenerating fixed diagrams...")
        
        # Regenerate the fixed diagrams
        import subprocess
        import sys
        
        for filename in fixed_files:
            script_name = filename
            try:
                print(f"🔄 Regenerating {script_name}...")
                result = subprocess.run([sys.executable, script_name], 
                                      capture_output=True, text=True, check=True)
                print(f"✅ {script_name} regenerated successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error regenerating {script_name}: {e}")
    
    print(f"\n🎯 Text overlap fixes complete!")

if __name__ == "__main__":
    main()