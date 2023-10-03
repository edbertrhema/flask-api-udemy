from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from datetime import timedelta

import os

from redis_bl import jwt_redis_blocklist
from blocklist import BLOCKLIST
from db import db

import models

from resources.items import blueprint as ItemBlueprint
from resources.stores import blueprint as StoreBlueprint
from resources.tags import blueprint as TagBlueprint
from resources.users import blueprint as UserBlueprint

ACCESS_EXPIRES = timedelta(hours=1)


def create_app(db_url=None):

    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","posgresql://postgres:root@localhost/flask-api-udemy")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "postgresql://postgres:root@localhost/flask-api-udemy"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app,db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"]= "62-ly9+5qvwo3b8a1l$q9=jyidgaj^zco6+5-fbnk-4@p3b3c3"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
    
    jwt = JWTManager(app)



    # Callback function to check if a JWT exists in the redis blocklist
    # @jwt.token_in_blocklist_loader
    # def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    #     jti = jwt_payload["jti"]
    #     token_in_redis = jwt_redis_blocklist.get(jti)
    #     return token_in_redis is not None

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "description": "The token has been revoked",
                "error": "token_revoked"
            }),401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return{
            jsonify({
                "description":"The token is not fresh",
                "error":"fresh_token_required",
            }),401,
        }

    @jwt.expired_token_loader
    def expired_token_loader(jwt_header, jwt_payload):
        return(
            jsonify({
                "message":"The token has expired",
                "error":"token_expired"
            }),401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify({
                "message":"signature verification failed",
                "error":"invalid_token"
            }),401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify({
                "description":"Reqest does not contain an access token",
                "error":"authoration_required"
            }),401,
        )

    # no longger use because using alembic flask-migrate
    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app