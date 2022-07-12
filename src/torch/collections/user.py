from click import DateTime
from flask_security import UserMixin
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from torch.collections.specimen import Institution
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


def save_user(id, first_name, last_name, institution_id):
    user = get_user(id)
    user.first_name = first_name
    user.last_name = last_name

    if institution_id is not None:
        institution = Institution.query.filter_by(id=institution_id).first()
        user.institution_id = institution.id
        user.institution_code = institution.code
    elif user.institution_code is not None:
        institution = Institution.query.filter_by(code=user.institution_code).first()
        user.institution_id = institution.id

    db.commit()


def toggle_user_active(id):
    user = User.query.get(id)
    user.active = 0 if user.active == 1 else 1

    db.session.commit()