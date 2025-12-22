import zlib
import requests
from pathlib import Path

PUML = r"""
@startuml
left to right direction
skinparam packageStyle rectangle
actor Eleveur as User
actor Veterinaire as Vet
actor System

package "Gestion des Bandes" {
  usecase "Créer / modifier bande" as UC1
  usecase "Consigner consommation" as UC2
  usecase "Consigner traitement" as UC3
  usecase "Voir détail bande" as UC4
}

package "Analyse & Dashboard" {
  usecase "Voir tableau de bord" as UC5
  usecase "Visualiser structure des coûts" as UC6
  usecase "Générer prédictions" as UC7
  usecase "Voir classement performances" as UC8
}

package "Automatisation & Notifications" {
  usecase "Terminaison automatique" as UC9
  usecase "Recevoir alertes sanitaires" as UC10
}

package "Assistant IA" {
  usecase "Dialoguer avec IA" as UC11
  usecase "Lancer analyse complète" as UC12
}

User --> UC1
User --> UC2
User --> UC3
User --> UC4
User --> UC5
User --> UC6
User --> UC7
User --> UC8
User --> UC11
User --> UC12

Vet --> UC3
Vet --> UC10

System --> UC9
System --> UC10

UC2 .down.> UC6 : data
UC3 .down.> UC10 : triggers
UC7 .down.> UC8 : data

note right of UC5
 Dashboard centralise :
  - consommation
  - mortalité
  - coûts (achat animaux inclus)
end note

@enduml
"""

OUT_PUML = Path('docs/usecases.puml')
OUT_PNG = Path('docs/usecases.png')

# PlantUML encoding functions (deflate + custom base64 per PlantUML)
# Implementation adapted from PlantUML docs / common snippets

CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

def encode6bit(b):
    if b < 0 or b >= 64:
        return '?'
    return CHARS[b]

def append3bytes(b1, b2, b3):
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return encode6bit(c1) + encode6bit(c2) + encode6bit(c3) + encode6bit(c4)

def plantuml_encode(plantuml_text: str) -> str:
    data = plantuml_text.encode('utf-8')
    compressed = zlib.compress(data, 9)
    # strip zlib header and checksum
    compressed = compressed[2:-4]
    res = []
    i = 0
    n = len(compressed)
    while i < n:
        b1 = compressed[i]
        b2 = compressed[i+1] if i+1 < n else 0
        b3 = compressed[i+2] if i+2 < n else 0
        res.append(append3bytes(b1, b2, b3))
        i += 3
    return ''.join(res)


def fetch_and_save_png(puml_text: str, out_png: Path):
    encoded = plantuml_encode(puml_text)
    url = f'https://www.plantuml.com/plantuml/png/{encoded}'
    print('Attempting GET:', url[:120] + ('...' if len(url) > 120 else ''))
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and r.headers.get('Content-Type','').startswith('image'):
            out_png.parent.mkdir(parents=True, exist_ok=True)
            out_png.write_bytes(r.content)
            print('Saved use-case PNG to', out_png)
            return True
        else:
            print('PlantUML GET failed', r.status_code, r.headers.get('Content-Type'))
            return False
    except Exception as e:
        print('GET request error:', e)
        return False


if __name__ == '__main__':
    OUT_PUML.parent.mkdir(parents=True, exist_ok=True)
    OUT_PUML.write_text(PUML, encoding='utf-8')
    print('Saved use-case PlantUML to', OUT_PUML)
    ok = fetch_and_save_png(PUML, OUT_PNG)
    if not ok:
        print('Failed to fetch PNG via GET. The PlantUML server may require consent or be unreachable.')
    else:
        print('Use-case PNG generated at', OUT_PNG)
