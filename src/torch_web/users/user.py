from flask_security import UserMixin
from torch_web import db, Base
from sqlalchemy import Table, Integer, Column, String, Boolean, DateTime, ForeignKey, select
from sqlalchemy.orm import relationship, backref, joinedload


roles_users = Table(
    "roles_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)


class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True)
    password = Column(String(150))
    first_name = Column(String(150))
    last_name = Column(String(150))
    active = Column(Boolean)
    confirmed_at = Column(DateTime)
    institution_id = Column(Integer, ForeignKey("institution.id"))
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    roles = relationship(
        "Role", secondary=roles_users, backref=backref("users", lazy="dynamic")
    )


def get_users(institution_id):
    return db.session.scalars(select(User).options(joinedload(User.roles)).filter(institution_id=institution_id)).all()


def get_user(user_id) -> User:
    return db.session.get(User, user_id)


def save_user(user_id, first_name, last_name, institution_id):
    user = get_user(user_id)

    user.first_name = first_name
    user.last_name = last_name

    print(last_name)

    if institution_id is not None:
        institution = Institution.query.filter_by(id=institution_id).first()
        user.institution_id = institution.id
        user.institution_code = institution.code
    elif user.institution_code is not None:
        institution = Institution.query.filter_by(code=user.institution_code).first()
        user.institution_id = institution.id

    db.session.commit()


def toggle_user_active(user_id):
    user = get_user(user_id)
    user.active = 0 if user.active == 1 else 1

    db.session.commit()
