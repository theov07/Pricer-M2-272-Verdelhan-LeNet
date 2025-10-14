from flask import Flask, render_template
from API.routes.routes import api_bp


app = Flask(__name__, 
           template_folder='API/web/templates',
           static_folder='API/web/static')


app.register_blueprint(api_bp)


@app.route('/')
def index():
    """Page principale avec l'interface utilisateur"""
    return render_template('index.html')


if __name__ == '__main__':
    print("🚀 Pricer Trinomial Pro - Application")
    print("🌐 Interface web: http://localhost:5001")
    print("🔗 API: http://localhost:5001/api/calculate")
    
    app.run(host='0.0.0.0', port=5001, debug=True)