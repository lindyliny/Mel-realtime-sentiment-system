from app import db


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512))
    name = db.Column(db.String(64))
    uid = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    city = db.Column(db.String(64))

    def __init__(self, tid, text, name, uid, date, city):
        self.id = tid
        self.text = text
        self.name = name
        self.uid = uid
        self.date = date
        self.city = city

    def add(self):
        dbtt = self.query.filter_by(id=self.id).first()
        if dbtt is None:
            db.session.add(self)
