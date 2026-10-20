from datetime import datetime, timezone

from sqlalchemy.ext.hybrid import hybrid_property

from config import bcrypt, db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    _password_hash = db.Column(db.String(128), nullable=False)

    workouts = db.relationship(
        "Workout",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        self._password_hash = hashed

    def authenticate(self, password):
        if not self._password_hash or not password:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    performed_on = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    user = db.relationship("User", back_populates="workouts")

    def __repr__(self):
        return f"<Workout {self.id} {self.name}>"
