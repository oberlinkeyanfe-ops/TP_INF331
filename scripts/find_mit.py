from pathlib import Path
b=Path('Backend/routes/dashboard.py').read_bytes()
for pat in [b'mit(5).all', b'li\nmit(5).all', b'li\r\nmit(5).all', b'limit(5).all']:
    print(pat, b.find(pat))
# show surrounding
idx=b.find(b'mit(5).all')
if idx!=-1:
    print(b[idx-60:idx+60])
else:
    print('not found')
