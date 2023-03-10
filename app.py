from flask import Flask, render_template
from db_connector import db_handler, search


def create_app():
    app = Flask(__name__)
    app.register_blueprint(db_handler)

    @app.route("/")
    def base():
        return search()
    return app



