from pathlib import Path
b=Path('Backend/routes/dashboard.py').read_bytes()
pat=b"@dashboard_bp.route('/bande/details/<int:bande_id>', methods=['GET'])"
i=b.find(pat)
print('i',i)
print(repr(b[i:i+800]))
print('\nTEXT:\n', b[i:i+800].decode('utf8', errors='replace'))
