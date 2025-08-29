"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin.setup_admin import setup_admin

from models import db
from routes.users import register_user_routes
from routes.posts import register_post_routes

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")

if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    sqlite_path = os.path.join(basedir, "test.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#compruebo que la base de datos se ha configurado correctamente
print(f"🚀 Starting app with DB: {app.config['SQLALCHEMY_DATABASE_URI']}")

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

with app.app_context():
    db.create_all()
    setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


register_user_routes(app)
register_post_routes(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
