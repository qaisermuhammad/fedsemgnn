import importlib.util as u

def has(name: str) -> bool:
    return u.find_spec(name) is not None

print("pypdf:", has("pypdf"))
print("pdfplumber:", has("pdfplumber"))
print("fitz (PyMuPDF):", has("fitz"))
print("pdfminer:", has("pdfminer"))
