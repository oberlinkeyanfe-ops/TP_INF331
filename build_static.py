from app import app
from flask_frozen import Freezer
import os

app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = 'static_build'

freezer = Freezer(app)

if __name__ == '__main__':
    print("🔨 Construction du site statique...")
    
    if not os.path.exists('static_build'):
        os.makedirs('static_build')
    
    freezer.freeze()
    print("✅ Site statique généré avec succès !")
