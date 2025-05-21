from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.secret_key = 'secret-key-2025'

    from app.controllers.main_controller import main
    from app.controllers.auth_controller import auth

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    return app