from flask import Flask, render_template
from API.routes.routes import api_bp
import os


app = Flask(__name__, 
           template_folder='API/web/templates',
           static_folder='API/web/static')


app.register_blueprint(api_bp)


@app.route('/')
def index():
    """Page principale avec l'interface utilisateur"""
    return render_template('index.html')


if __name__ == '__main__':
    # Port pour Railway (variable d'environnement PORT)
    port = int(os.environ.get('PORT', 5001))
    
    print("🚀 Pricer Trinomial Pro - Application")
    print(f"🌐 Interface web: http://0.0.0.0:{port}")
    
    # Mode debug désactivé en production
    debug_mode = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)