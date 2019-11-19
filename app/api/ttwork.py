from flask_restful import Api, Resource
from flask import jsonify, request
from app import db
from app.models import tweet
from app.api import api
from app.utils import ttapi
import datetime
from geojson import Feature, Point, FeatureCollection

api_ttwork = Api(api)


class TweetByCity(Resource):
    def post(self):
        req = request.get_json()
        try:
            t = ttapi.tweet()
            city = req['city']
            if city != '':
                tts = t.get_citytweet(city)
                if tts is None:
                    return jsonify({'code': 0, 'data': ''})

                for tt in tts:
                    newtt = tweet.Tweet(tid=tt['id'], text=tt['text'], name=tt['name'], uid=tt['uid'],
                                        date=tt['date'],
                                        region=tt['place'], senti=tt['senti'])
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
                                    region=tt['place'], senti=tt['senti'])
                newtt.add()
            db.session.commit()
            return jsonify({'cnt': len(tts), 'data': tts})
        except Exception as err:
            return jsonify({'code': -1, 'data': str(err)})
        finally:
            db.session.close()


class GetAreaHistorySenti(Resource):
    def post(self):
        try:
            req = request.get_json()
            switch = {"year": self.year, "month": self.month, "week": self.week}
            period = req['period'].lower()
            timepoint = []
            f = switch.get(period)
            if f is None:
                return jsonify({})
            f(timepoint)
            timepoint = timepoint[::-1]
            areas = req['areas'].split(",")

            disptp = []
            for tp in timepoint:
                if period == 'week':
                    disptp.append(tp['s'])
                elif period == 'year':
                    disptp.append(tp['s'][:7])
            if period == 'month':
                disptp.append('week1')
                disptp.append('week2')
                disptp.append('week3')
                disptp.append('week4')

            motions = []
            for area in areas:
                aresmotion = {'area': area}
                motion = []

                sname = area + ", Melbourne"
                geo = tweet.Areas.get(area)
                tts = {}
                t = ttapi.tweet()

                if geo is None:
                    tts = t.get_citytweet(sname)
                else:
                    tts = t.get_geotweet(geo.lat, geo.long)

                sentiMax = 0.0
                ttback = len(tts)
                for tt in tts:
                    sentiMax += tt['senti']

                for date in timepoint:
                    results = tweet.TweetHistory.avg_range(date['s'], date['e'], area)
                    ret = list(filter(lambda o: o.region == area, results))
                    if len(ret) == 0:
                        motion.append(0.0)
                    else:
                        motion.append(ret[0].senti)

                prev = motion[len(motion) - 1]
                
                if prev == 0.0 and ttback > 0:
                    prev = sentiMax / ttback
                if ttback > 0:
                    motion[len(motion) - 1] = (prev + sentiMax / ttback) / 2

                aresmotion['emotion'] = motion
                motions.append(aresmotion)

            return jsonify({'timePoint': disptp, 'areaEmotion': motions})
        except Exception as err:
            return jsonify({'code': -1, 'data': str(err)})
        finally:
            db.session.close()

    def year(self, timepoint):
        for num in range(12):
            timepoint.append(
                {'s': (datetime.datetime.now() + datetime.timedelta(days=-30 * num - 29)).strftime("%Y-%m-%d"),
                 'e': (datetime.datetime.now() + datetime.timedelta(days=-30 * num)).strftime("%Y-%m-%d")})

    def month(self, timepoint):
        for num in range(4):
            timepoint.append(
                {'s': (datetime.datetime.now() + datetime.timedelta(days=-7 * num - 6)).strftime("%Y-%m-%d"),
                 'e': (datetime.datetime.now() + datetime.timedelta(days=-7 * num)).strftime(
                     "%Y-%m-%d")})

    def week(slef, timepoint):
        for num in range(7):
            timepoint.append({'s': (datetime.datetime.now() + datetime.timedelta(days=-1 * num)).strftime("%Y-%m-%d"),
                              'e': (datetime.datetime.now() + datetime.timedelta(days=-1 * num)).strftime("%Y-%m-%d")})


class QueryAreasByName(Resource):
    def post(self):
        try:
            req = request.get_json()
            queryParam = req['name']
            if queryParam == '':
                return jsonify([])
            results = tweet.Areas.query(queryParam)
            arr = []
            for o in results:
                arr.append(o.name)
            return jsonify(arr)
        except Exception as err:
            return jsonify({'code': -1, 'data': str(err)})
        finally:
            db.session.close()


class AllAreaEmotionInGeo(Resource):
    def post(self):
        try:
            history = tweet.TweetHistory.avg_all()
            areas = tweet.Areas.get_all()
            features = []

            for his in history:
                ret = list(filter(lambda o: o.name == his.region, areas))

                if len(ret) == 0:
                    f = Feature(geometry=Point(0, 0), id=-1, properties={'emotion': his.senti, 'area': his.region})
                else:
                    f = Feature(geometry=Point((ret[0].long, ret[0].lat)), id=ret[0].id,
                                properties={'emotion': his.senti, 'area': his.region})
                features.append(f)
            fc = FeatureCollection(features)
            return jsonify(fc)
        except Exception as err:
            return jsonify({'code': -1, 'data': str(err)})
        finally:
            db.session.close()


api_ttwork.add_resource(TweetByCity, '/bycityname', endpoint='bycityname')
api_ttwork.add_resource(TweetByGeo, '/bygeo', endpoint='bygeo')
api_ttwork.add_resource(GetAreaHistorySenti, '/multiAreaEmotion', endpoint='multiAreaEmotion')
api_ttwork.add_resource(QueryAreasByName, '/queryAreasByName', endpoint='queryAreasByName')
api_ttwork.add_resource(AllAreaEmotionInGeo, '/allAreaEmotionInGeo', endpoint='allAreaEmotionInGeo')
