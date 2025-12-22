import os
p='docs/test_report.pdf'
if not os.path.exists(p):
    print('File not found:', p)
    raise SystemExit(1)
sz=os.path.getsize(p)
print('Size:', sz, 'bytes')
with open(p,'rb') as f:
    head=f.read(20)
print('Head bytes:', head[:8])
try:
    print('Head as text:', head.decode('latin1', errors='replace'))
except Exception as e:
    print('decode error', e)
