import sys
import json
# Ensure project root is on path for 'Backend' package imports when run from scripts/
sys.path.insert(0, r"c:\Users\hp\TP_INF331")
# Also ensure Backend folder is on path for local imports like `modeles`
sys.path.insert(0, r"c:\Users\hp\TP_INF331\Backend")
from Backend.app import app

with app.test_client() as c:
    # set session eleveur_id=2
    with c.session_transaction() as sess:
        sess['eleveur_id'] = 2
    resp = c.get('/dashboard/performance/bandes')
    print('GET /dashboard/performance/bandes ->', resp.status_code)
    try:
        data = resp.get_json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print('Failed parse JSON:', e)

    resp2 = c.get('/dashboard/global-v2')
    print('\nGET /dashboard/global-v2 ->', resp2.status_code)
    try:
        data2 = resp2.get_json()
        perf = data2.get('performance') if isinstance(data2, dict) else None
        print('performance length:', len(perf) if perf else 0)
        if perf and len(perf) > 0:
            print('\nsample performance[0]:')
            print(json.dumps(perf[0], indent=2, ensure_ascii=False))
    except Exception as e:
        print('Failed parse JSON 2:', e)

    # Test PDF report endpoint and save result
    print('\nGET /dashboard/report/pdf ->')
    rpt = c.get('/dashboard/report/pdf')
    print('status', rpt.status_code, 'content-type', rpt.content_type)
    if rpt.status_code == 200 and rpt.content_type == 'application/pdf':
        open('docs/test_report.pdf', 'wb').write(rpt.get_data())
        print('Saved docs/test_report.pdf')
    else:
        print('PDF endpoint failed or returned non-pdf, body snippet:')
        try:
            print(rpt.get_data(as_text=True)[:400])
        except Exception:
            pass
