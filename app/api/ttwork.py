from flask_restful import Api, Resource
from flask import jsonify, request
from app import db
from app.models import tweet
from app.api import api
from app.utils import ttapi

api_ttwork = Api(api)


class TweetByCity(Resource):
    def post(self):
        req = request.get_json()
        try:
            t = ttapi.tweet()
            city = req['city']
            if city != '':
                tts = t.get_tweet(city)
                for tt in tts:
                    newtt = tweet.Tweet(tid=tt['id'], text=tt['text'], name=tt['name'], uid=tt['uid'],
                                        date=tt['date'],
                                        city=tt['place'])
                    newtt.add()
                db.session.commit()
                return jsonify({'cnt': len(tts), 'data': tts})
            else:
                return jsonify({'code': 0, 'data': ''})
        except Exception as err:
            return jsonify({'code': -1, 'data': str(err)})
        finally:
            db.session.close()


class TweetByGeo(Resource):
    def post(self):
        req = request.get_json()
        try:
            t = ttapi.tweet()
            lat = float(req['lat'])
            long = float(req['long'])
            tts = t.get_geotweet(lat, long)
            for tt in tts:
                newtt = tweet.Tweet(tid=tt['id'], text=tt['text'], name=tt['name'], uid=tt['uid'],
                                    date=tt['date'],
                                    city=tt['place'])
                newtt.add()
            db.session.commit()
            return jsonify({'cnt': len(tts), 'data': tts})
        except Exception as err:
            return jsonify({'code': -1, 'data': str(err)})
        finally:
            db.session.close()


api_ttwork.add_resource(TweetByCity, '/bycityname', endpoint='bycityname')
api_ttwork.add_resource(TweetByGeo, '/bygeo', endpoint='bygeo')
