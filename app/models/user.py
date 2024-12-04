from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    validated = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<User {self.email}>'
