
from flask import Flask, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchemas, StoreUpdateSchemas


blueprint = Blueprint("stores", __name__, description= "Operation on stores")

@blueprint.route("/stores")
class Store(MethodView):

    @blueprint.response(200, StoreSchemas(many=True))
    def get(self):

        return StoreModel.query.all()

    @blueprint.arguments(StoreSchemas)
    @blueprint.response(200, StoreSchemas)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()

            return store
        except IntegrityError:
            abort(400, message="A store with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An Error occured while insertting the item.")
        

@blueprint.route("/stores/<int:store_id>")
class StoreID(MethodView):

    @blueprint.response(200, StoreSchemas)
    def get(self, store_id):

        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required(fresh=True)
    @blueprint.response(204, StoreSchemas)
    def delete(self, store_id):

        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return store

    @blueprint.arguments(StoreUpdateSchemas)
    @blueprint.response(200, StoreSchemas)        
    def put(self,store_data, store_id):

        store = StoreModel.query.get(store_id)
        if store:
            store.name = store_data["name"]
        else:
            store = StoreModel(id=store_id, **store_data) 

        db.session.add(store)
        db.session.commit()            

        return store   
