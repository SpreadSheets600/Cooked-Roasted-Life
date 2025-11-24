import os
from flask import Flask
from .config import Config
from .routes import main_bp, auth_bp, api_bp
from .models.database import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Load Base Config
    app.config.from_object(Config)

    # Load Instance Config if Present (Secrets Override)
    instance_cfg_path = os.path.join(app.instance_path, "config.py")
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        if os.path.exists(instance_cfg_path):
            app.config.from_pyfile("config.py", silent=True)
    except OSError:
        pass

    if test_config:
        app.config.update(test_config)

    # Initialize Database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Simple Health Endpoint
    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app
