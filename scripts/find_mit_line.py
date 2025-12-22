from pathlib import Path
lines=Path('Backend/routes/dashboard.py').read_bytes().splitlines()
for i,l in enumerate(lines, start=1):
    if l.strip()==b'mit(5).all()':
        print('found at', i, repr(l))
        # print previous line
        print('prev:', i-1, repr(lines[i-2]))
        break
else:
    print('not found')
