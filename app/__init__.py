import os
from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import main_bp, auth_bp, api_bp
from .models.database import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(Config)

    instance_cfg_path = os.path.join(app.instance_path, "config.py")
    try:
        os.makedirs(app.instance_path, exist_ok=True)

        if os.path.exists(instance_cfg_path):
            app.config.from_pyfile("config.py", silent=True)

    except OSError:
        pass

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    cors_origins = app.config.get("FRONTEND_ORIGIN") or "*"
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=True,
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    return app
