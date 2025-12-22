import re
from pathlib import Path
import requests

MODELS_PY = Path('Backend/modeles/models.py')
OUT_PNG = Path('docs/models_uml.png')

CLASS_RE = re.compile(r'^class\s+(\w+)\(.*\):')
COLUMN_RE = re.compile(r"\s*(\w+)\s*=\s*db\.Column\(([^)]*)\)")
FK_RE = re.compile(r"ForeignKey\('(?P<table>\w+)\.(?P<col>\w+)'\)")
REL_RE = re.compile(r"\s*(\w+)\s*=\s*db\.relationship\('(?P<class>\w+)'(?:,\s*backref='(?P<back>\w+)')?")


def parse_models(path: Path):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    classes = {}
    cur = None
    for ln in lines:
        m = CLASS_RE.match(ln)
        if m:
            cur = m.group(1)
            classes[cur] = {'attrs': [], 'cols': [], 'rels': []}
            continue
        if cur is None:
            continue
        mcol = COLUMN_RE.search(ln)
        if mcol:
            attr = mcol.group(1)
            rest = mcol.group(2)
            fk = FK_RE.search(rest)
            classes[cur]['cols'].append((attr, rest.strip(), fk.groupdict() if fk else None))
            continue
        mrel = REL_RE.search(ln)
        if mrel:
            attr = mrel.group(1)
            classes[cur]['rels'].append({'attr': attr, 'target': mrel.group('class'), 'back': mrel.group('back')})
    return classes


def build_plantuml(classes: dict):
    parts = ['@startuml', 'skinparam classAttributeIconSize 0', 'hide empty members']
    # classes with attributes
    for cname, info in classes.items():
        parts.append(f'class {cname} {{')
        # columns
        for col, spec, fk in info['cols']:
            parts.append(f'  {col} : {spec}')
        parts.append('}')
    # relationships from FK and relationship()
    for cname, info in classes.items():
        # relationships from columns with FK
        for col, spec, fk in info['cols']:
            if fk:
                target_table = fk['table']
                # Try to map table name to class name (simple singular/plural heuristics) - choose matching class name ignoring case
                target_cls = None
                for k in classes.keys():
                    if k.lower().startswith(target_table.lower()) or target_table.lower().startswith(k.lower()):
                        target_cls = k
                        break
                if not target_cls:
                    # fallback capitalize
                    target_cls = target_table.capitalize()
                parts.append(f'{cname} --> {target_cls} : {col}\n(FK)')
        # relationships via db.relationship
        for r in info['rels']:
            parts.append(f'{cname} "1" -- "*" {r["target"]} : {r["attr"]}')
    parts.append('@enduml')
    return '\n'.join(parts)


def post_plantuml_and_save(plantuml_text: str, out_path: Path):
    url = 'http://www.plantuml.com/plantuml/png/'
    headers = {'Content-Type': 'text/plain'}
    attempts = 3
    for i in range(1, attempts + 1):
        try:
            print(f'Attempt {i}/{attempts} to POST PlantUML...')
            r = requests.post(url, data=plantuml_text.encode('utf-8'), headers=headers, timeout=30)
            ct = r.headers.get('Content-Type', '')
            if r.status_code == 200 and ct.startswith('image'):
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(r.content)
                print('Saved UML PNG to', out_path)
                return
            else:
                print(f'Attempt {i}: unexpected response (status={r.status_code}, content-type={ct})')
                # small heuristic: show start of body if not too long
                snippet = (r.text[:400] + '...') if r.text and len(r.text) > 400 else r.text
                print('Response snippet:', snippet)
        except Exception as e:
            print(f'Attempt {i} failed: {e}')
        if i < attempts:
            import time
            time.sleep(2)
    print('All attempts failed: server did not return an image. Consider retrying later or using encoded GET fallback.')


if __name__ == '__main__':
    classes = parse_models(MODELS_PY)
    pu = build_plantuml(classes)
    print('Generated PlantUML (snippet):')
    print('\n'.join(pu.splitlines()[:40]))
    # Save PlantUML source for review
    puml_path = Path('docs/models.puml')
    puml_path.parent.mkdir(parents=True, exist_ok=True)
    puml_path.write_text(pu, encoding='utf-8')
    print('Saved PlantUML source to', puml_path)
    post_plantuml_and_save(pu, OUT_PNG)
