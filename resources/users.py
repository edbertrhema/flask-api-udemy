from flask import Flask, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token,jwt_required, get_jwt, jwt_required, create_refresh_token, get_jwt_identity

from redis_bl import jwt_redis_blocklist
from db import db
from blocklist import BLOCKLIST

from models import UserModel
from schemas import UserSchema



blueprint = Blueprint("Users","users", description = "Operation on users")

@blueprint.route("/register")
class UserRegister(MethodView):
    @blueprint.arguments(UserSchema)
    def post(self, user_data):

        user = UserModel(
            name = user_data["name"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )

        db.session.add(user)
        db.session.commit()

        return {"message":"user created successfully."},201

@blueprint.route("/users/<int:user_id>")
class User(MethodView):
    
    @blueprint.response(200,UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blueprint.response(204)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

@blueprint.route("/login")
class UserLogin(MethodView):

    @blueprint.arguments(UserSchema)
    def post(self,user_data):
        user = UserModel.query.filter(
            UserModel.name == user_data["name"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token,
                    "refresh_token": refresh_token
            }

        abort(401, message="invalid username or password")

@blueprint.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"message": new_token}

@jwt_required()
@blueprint.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]

        BLOCKLIST.add(jti)
        # jwt_redis_blocklist.set(jti, "")
        return {"message":"Succesfully logged out"}



