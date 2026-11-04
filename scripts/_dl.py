import sys,urllib.request,ssl
ctx=ssl.create_default_context()
for spec in sys.argv[1:]:
    name,url=spec.split('=',1)
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0) Chrome/130','Accept':'*/*'}),timeout=120,context=ctx)
        b=r.read(); open(name,'wb').write(b); print(name,r.status,r.headers.get('content-type'),len(b),b[:5])
    except Exception as e: print(name,'ERR',e)
