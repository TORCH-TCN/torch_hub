from click import DateTime
from flask_security import UserMixin
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from torch.config.database.TorchDatabase import Entity, db


roles_users = Table(
    "roles_users",
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)


class User(Entity, UserMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True)
    password = Column(String(150))
    first_name = Column(String(150))
    last_name = Column(String(150))
    active = Column(Boolean)
    confirmed_at = Column(DateTime)
    institution_code = Column(String(10))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    roles = relationship(
        "Role", secondary=roles_users, backref=backref("users", lazy="dynamic")
    )


def get_user(id) -> User:
    return User.query.filter_by(id=id).first()


def save_user(id, first_name, last_name):
    user = get_user(id)
    user.first_name = first_name
    user.last_name = last_name
    db.commit()
