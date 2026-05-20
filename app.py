from flask import Flask, redirect, url_for

from routes.settings import settings_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(settings_bp)

    @app.route("/")
    def home():
        return redirect(url_for("settings.settings_index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
