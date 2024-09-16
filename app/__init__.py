from flask_migrate import Migrate
from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
 
# Inicialización de las extensiones
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
 
def create_app():
    app = Flask(__name__)
    
    # Configuración de la aplicación desde el archivo config.py
    app.config.from_object(Config)
    
    # Inicializar las extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Registrar los blueprints
    from app.lugar import bp as lugar_bp
    app.register_blueprint(lugar_bp, url_prefix='/lugares')
 
    from app.persona import bp as persona_bp
    app.register_blueprint(persona_bp, url_prefix='/personas')
 
    
    @app.route('/')
    def home():
        return render_template('index.html')
 
    return app