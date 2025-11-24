from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import hashlib

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    picture = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    roasts = db.relationship(
        "Roast", back_populates="user", cascade="all, delete-orphan"
    )
    recent_roasts = db.relationship(
        "RecentRoast", back_populates="user", cascade="all, delete-orphan"
    )

    def get_avatar(self):
        if self.picture and self.picture.startswith("http"):
            return self.picture

        seed = hashlib.md5(self.email.encode()).hexdigest()
        return f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "picture": self.get_avatar(),
        }


class Roast(db.Model):
    __tablename__ = "roasts"

    id = db.Column(db.String(8), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    roast_text = db.Column(db.Text, nullable=False)
    sources = db.Column(db.JSON)
    raw_data = db.Column(db.JSON)
    inputs = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship("User", back_populates="roasts")

    def to_dict(self):
        return {
            "id": self.id,
            "roast": self.roast_text,
            "sources": self.sources,
            "raw": self.raw_data,
            "inputs": self.inputs,
            "timestamp": self.created_at.isoformat(),
            "user": self.user.to_dict() if self.user else None,
            "is_public": self.is_public,
        }


class RecentRoast(db.Model):
    __tablename__ = "recent_roasts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    roast_id = db.Column(db.String(8), db.ForeignKey("roasts.id"), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="recent_roasts")
    roast = db.relationship("Roast")

    __table_args__ = (
        db.UniqueConstraint("user_id", "roast_id", name="unique_user_roast"),
    )
