from datetime import timedelta, datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    purchase_date = db.Column(db.Date)
    light_conditions = db.Column(db.String(64))
    watering_frequency = db.Column(db.String(64))
    fertilizing_frequency = db.Column(db.String(64))
    notes = db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    owner = db.relationship("User", back_populates="plants")

    def next_watering_date(self):
        freq_map = {
            "daily": 1,
            "every 3 days": 3,
            "weekly": 7,
            "bi-weekly": 14,
            "monthly": 30,
        }
        if self.watering_frequency not in freq_map:
            return None
        days_since_purchase = (datetime.utcnow().date() - self.purchase_date).days
        if days_since_purchase < 0:
            return None
        days_to_next_watering = freq_map[self.watering_frequency] - (
            days_since_purchase % freq_map[self.watering_frequency]
        )
        return datetime.utcnow().date() + timedelta(days=days_to_next_watering)


User.plants = db.relationship("Plant", order_by=Plant.id, back_populates="owner")
