from pathlib import Path
b=Path('Backend/routes/dashboard.py').read_bytes()
pat=b'Traitement.query'
idx=b.find(pat)
print('idx', idx)
print(b[idx:idx+200])
# show hex with escapes
print('\nHex:')
print(' '.join(hex(x) for x in b[idx:idx+200]))
