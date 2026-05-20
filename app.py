import os

from flask import Flask, redirect, url_for

from routes.campaigns import campaigns_bp
from routes.settings import settings_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

    app.register_blueprint(settings_bp)
    app.register_blueprint(campaigns_bp)

    @app.route("/")
    def home():
        return redirect(url_for("campaigns.campaigns_index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
