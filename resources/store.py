from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.store import StoreModel
from schemas import StoreSchema


blp = Blueprint("Stores", "stores", description="Operations on stores")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store 

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id) 
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        # retrieve all stores in table
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data) # return dict into kwargs

        try:
            db.session.add(store)
            db.session.commit() # save to disc
        except IntegrityError:
            # is raised when a store is created that already exists.
            abort(
                400,
                message="An error occured creating the store"
            )
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting items into the db.")
        return store
