#imports
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates


db = SQLAlchemy()


class Ticket(db.Model, SerializerMixin):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    created_by = db.Column(db.String)
    description = db.Column(db.String)
    response = db.Column(db.String)
    status = db.Column(db.String, server_default="New")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @validates('created_by')
    def validate_created_by(self, key, created_by):
        if "@" in created_by and not None:
            return created_by
        else:
            raise Exception("Not a valid email input")

    @validates('title')
    def validate_title(self, key, title):
        if title is None or title == "":
            raise ValueError("Title must be provided.")
        return title

    @validates('description')
    def check_description(self, key, description):
        if description is None or description == "":
            raise ValueError("Description must be provided.")
        return description