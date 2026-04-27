import shutil
import os
from pathlib import Path

def clear_graphs_folder():
    base = Path('graphs')
    if not base.exists():
        return
    for item in base.rglob('*'):
        if item.is_file() and (item.suffix.lower() in ['.png', '.pdf', '.svg', '.jpg']):
            try:
                item.unlink()
            except Exception as e:
                print(f"[WARNING] Could not delete {item}: {e}")

# Call this at the very top of generate_all_graphs.py before any plotting
clear_graphs_folder()
