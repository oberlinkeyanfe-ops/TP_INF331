from pathlib import Path
lines=Path('Backend/routes/dashboard.py').read_text(encoding='utf8').splitlines()
for i,l in enumerate(lines[-100:], start=len(lines)-99):
    print(i+1, l)
print('TOTAL LINES', len(lines))
