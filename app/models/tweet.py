from app import db
from sqlalchemy.sql import func
from sqlalchemy import and_


class Tweet(db.Model):
    __tablename__ = 'tweets'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(512))
    name = db.Column(db.String(64))
    uid = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    region = db.Column(db.String(64))
    senti = db.Column(db.FLOAT)

    def __init__(self, tid, text, name, uid, date, region, senti):
        self.id = tid
        self.text = text
        self.name = name
        self.uid = uid
        self.date = date
        self.region = region
        self.senti = senti

    def add(self):
        dbtt = self.query.filter_by(id=self.id).first()
        if dbtt is None:
            db.session.add(self)


class TweetHistory(db.Model):
    __tablename__ = 'tweets_history'

    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer)
    date = db.Column(db.String)
    region = db.Column(db.String(64))
    senti = db.Column(db.FLOAT)
    tweet = db.Column(db.String)

    def __init__(self, tid, date, region, senti, tweet):
        self.tid = tid
        self.date = date
        self.region = region
        self.senti = senti
        self.tweet = tweet

    def add(self):
        dbtt = self.query.filter_by(tid=self.tid).first()
        if dbtt is None:
            db.session.add(self)

    @staticmethod
    def avg(dates, areas):
        results = db.session.query(func.avg(TweetHistory.senti).label('senti'), TweetHistory.date,
                                   TweetHistory.region).filter(and_(TweetHistory.region.in_(areas),
                                                                    TweetHistory.date.in_(dates))).group_by(
            TweetHistory.date,
            TweetHistory.region).all()
        return results

    @staticmethod
    def avg_range(start, end, areas):
        results = db.session.query(func.avg(TweetHistory.senti).label('senti'),
                                   TweetHistory.region).filter(and_(TweetHistory.region==areas,
                                                                    TweetHistory.date >= start,
                                                                    TweetHistory.date <= end)).group_by(
            TweetHistory.region).all()
        return results

    @staticmethod
    def avg_all():
        results = db.session.query(func.avg(TweetHistory.senti).label('senti'),
                                   TweetHistory.region).group_by(TweetHistory.region).all()
        return results


class Areas(db.Model):
    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    long = db.Column(db.FLOAT)
    lat = db.Column(db.FLOAT)

    @staticmethod
    def query(name):
        q = '%' + name + '%'
        results = db.session.query(Areas.name).filter(Areas.name.like(q)).all()
        return results

    @staticmethod
    def get(name):
        return db.session.query(Areas).filter(Areas.name == name).first()

    @staticmethod
    def get_all():
        return db.session.query(Areas).all()
