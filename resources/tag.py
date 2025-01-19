from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models.store import StoreModel 
from models.tag import TagModel
from models.item import ItemModel
from models.item_tags import ItemsTags
from schemas import TagSchema, TagAndItemSchema


blp = Blueprint("Tags", "tags", description="Operations on tags")


@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        # since tags is lazy dynamic, a query, we have to do .all()
        # This kind of interaction with the db is much simpler than using
        # the TagModel -> no filter logic required
        return store.tags.all()

    @blp.arguments(TagSchema)# -> post input
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)
        # store_id=store_id: its always better to use the info from
        # the url instead to take it out of the data
        if TagModel.query.filter(TagModel.store_id == store_id,
                                 TagModel.name == tag_data["name"]).first():
            abort(400, message="A tag with that name already exists in that store.")

        try:
            db.session.add(tag)
            db.session.commit()

        except IntegrityError as e:
            abort(
                500,message=f"Actually, it is not possible to assign a tag to multiple stores."\
                    f"\nOriginal message: {str(e)}"
            )

        except SQLAlchemyError as e:
            abort(
                500, message=str(e)
            )
        return tag
    
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        # put the tags into a list
        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting tags.")

        return tag
    

    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        # put the tags into a list
        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while removing tags.")

        return {"message": "Item removed from tag", 
                "item": item,
                "tag": tag}
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted."}
    )
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any items, then try again."
        )

# not in course    
@blp.route("/tag")
class TagList(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        # retrieve all stores in table
        return TagModel.query.all()
    
    # @blp.arguments(TagSchema)
    # @blp.response(201, TagSchema)
    # def post(self, tag_data):
    #     tag = TagModel(**tag_data) # return dict into kwargs

    #     try:
    #         db.session.add(tag)
    #         db.session.commit() # save to disc
    #     except SQLAlchemyError:
    #         abort(500, message="An error occured while inserting tags into the db.")
    #     return tag