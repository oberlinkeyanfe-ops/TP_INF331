from pathlib import Path
p=Path('Backend/routes/dashboard.py')
b=p.read_bytes()
orig=b
replacements=[b'li\r\nmit(5).all()', b'li\nmit(5).all()', b'li\rmit(5).all()']
fixed=False
for rep in replacements:
    if rep in b:
        print('Found pattern:', rep)
        b=b.replace(rep, b'limit(5).all()')
        fixed=True
if fixed:
    backup=p.with_suffix('.py.bak')
    backup.write_bytes(orig)
    p.write_bytes(b)
    print('Fixed and wrote file; backup at', backup)
else:
    print('No known broken pattern found')
