from flask import Flask
from routes.recommend import recommend_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(recommend_bp, url_prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    app.run()
