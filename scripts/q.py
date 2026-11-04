import sys,re
sys.path.insert(0,'scripts')
from lib_pdf import pages
for spec in sys.argv[1:]:
    doc,rx=spec.split('::',1)
    pg=pages(f'raw/programas/{doc}.pdf'); hits=[]
    for i,p in enumerate(pg,1):
        t=re.sub(r'-\s*\n\s*(?=[a-záéíóúñ])','',p); t=re.sub(r'\s+',' ',t)
        for s in re.split(r'(?<=[.;:])\s+(?=[A-ZÁÉÍÓÚÑ•●·\d])|•|●',t):
            s=s.strip(' •●·-')
            if 50<=len(s)<=460 and re.search(rx,s,re.I): hits.append((abs(len(s)-180),i,s))
    hits.sort()
    print(f'## {doc} /{rx}/ {len(hits)}')
    for _,i,s in hits[:2]: print(f' p{i}: {s[:330]}')
