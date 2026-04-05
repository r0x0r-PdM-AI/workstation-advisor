import os

from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from models.user import User


bcrypt = Bcrypt()
login_manager = LoginManager()

# Blueprint imports follow extension declarations to avoid circular import
from routes.auth import auth_bp
from routes.profiles import profiles_bp
from routes.recommend import recommend_bp


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Unauthorised"}), 401

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))

    app.register_blueprint(recommend_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profiles_bp, url_prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    app.run()
