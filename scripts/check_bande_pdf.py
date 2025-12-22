import sys, os
sys.path.insert(0, r"c:\Users\hp\TP_INF331")
sys.path.insert(0, r"c:\Users\hp\TP_INF331\Backend")
from Backend.app import app
band_id = 705
with app.test_client() as c:
    with c.session_transaction() as s:
        s['eleveur_id'] = 2
    r = c.get(f'/dashboard/report/bande/{band_id}/pdf')
    print('status', r.status_code, 'content-type', r.content_type)
    if r.status_code == 200 and r.content_type == 'application/pdf':
        path = f'docs/test_bande_{band_id}.pdf'
        open(path, 'wb').write(r.get_data())
        print('Saved', path, 'size', os.path.getsize(path))
    else:
        print('Body:', r.get_data(as_text=True)[:800])
