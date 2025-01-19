from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
# SQLAlchemyError: Base Error from which all 
# specific Alchemy Errors are inheritted

from db import db
from models.item import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required() # indicating that a token is required
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        # retrieve data from the db
        item = ItemModel.query.get_or_404(item_id) 
        # from db.Model class -> flask sqlAlchemy
        return item

    @jwt_required() # indicating that a token is required
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id) 
        db.session.delete(item)
        db.session.commit()
        return {"message":"Item deleted."}
    
    @blp.arguments(ItemUpdateSchema) # whenever you use the arguments operator, the input gets to the front of inputs
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id) 
        # Make sure that request is idempotent
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)
            # make sure that you use the id that is passed through the url

        db.session.add(item)
        db.session.commit() # save to disc

        return item



@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True)) # to input multiple item schema
    def get(self):
        # retrieve all items from table as list (use Alchemy)
        return ItemModel.query.all()
    
    @jwt_required() # indicating that a token is required
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data) # return dict into kwargs

        try:
            db.session.add(item)
            db.session.commit() # save to disc
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting items into the db.")
        return item

