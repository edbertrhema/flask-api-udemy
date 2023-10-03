from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from sqlalchemy.exc import SQLAlchemyError

from models import ItemModel
from db import db
from schemas import ItemSchemas,ItemUpdateSchemas


blueprint = Blueprint("items", __name__, description= "Operation on items")

@blueprint.route("/items")
class Item(MethodView):

    @jwt_required()
    @blueprint.response(200, ItemSchemas(many=True))
    def get(self):

        return ItemModel.query.all()

    @jwt_required()
    @blueprint.arguments(ItemSchemas)
    @blueprint.response(201, ItemSchemas)
    def post(self, item_data):

        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An Error occured while insertting the item.")
       
        return item



@blueprint.route("/items/<int:item_id>")
class ItemID(MethodView):

    @blueprint.response(200, ItemSchemas)
    def get(self, item_id):

        item = ItemModel.query.get_or_404(item_id)
        return item

    @blueprint.response(204, ItemSchemas)
    def delete(self, item_id):

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return item

    @blueprint.arguments(ItemUpdateSchemas)
    @blueprint.response(200, ItemSchemas)
    def put(self, item_data , item_id):
        item = ItemModel.query.get(item_id)

        if item:
            item.name = item_data["name"]
            item.price = item_data["price"]
        else:
            item = ItemModel(id=item_id, **item_data) 

        db.session.add(item)
        db.session.commit()        
        return item   
