import re, subprocess, os, unicodedata
def pages(pdf):
    txt = pdf[:-4] + '.utf8.txt'
    if not os.path.exists(txt):
        subprocess.run(['pdftotext', '-enc', 'UTF-8', pdf, txt], check=True)
    return open(txt, encoding='utf-8', errors='replace').read().split('\f')
def norm(s):
    """Normaliza para comparar citas: une cortes de línea y guiones de maquetación, sin alterar palabras."""
    s = unicodedata.normalize('NFKC', s).replace('­', '')
    s = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', s)
    s = re.sub(r'[“”«»"]', '"', s).replace('’', "'")
    return re.sub(r'\s+', ' ', s).strip().lower()
