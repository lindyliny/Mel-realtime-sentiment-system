import tweepy
import config
import datetime
from textblob import TextBlob


class tweet:
    def get_citytweet(self, city_name):
        auth = tweepy.OAuthHandler(config.TwitterConfig.Customer_Key, config.TwitterConfig.Customer_Secret)
        auth.set_access_token(config.TwitterConfig.Token_Key, config.TwitterConfig.Token_Secret)
        api = tweepy.API(auth)
        if config.TwitterConfig.Proxy != '':
            api = tweepy.API(auth, proxy=config.TwitterConfig.Proxy)

        places = api.geo_search(query=city_name, granularity="city")
        if len(places) == 0:
            return
        place_id = places[0].id
        tweets = api.search(q="place:%s" % place_id,
                            until=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                            count=100, result_type="recent")
        results = []
        for tweet in tweets:
            results.append({'id': tweet.id, 'text': tweet.text, 'name': tweet.user.name, 'uid': tweet.user.id,
                            'date': tweet.created_at, 'place': tweet.place.name, 'senti': self.get_senti(tweet.text)})
        return results

    def get_geotweet(self, lat, long):
        auth = tweepy.OAuthHandler(config.TwitterConfig.Customer_Key, config.TwitterConfig.Customer_Secret)
        auth.set_access_token(config.TwitterConfig.Token_Key, config.TwitterConfig.Token_Secret)
        api = tweepy.API(auth)
        if config.TwitterConfig.Proxy != '':
            api = tweepy.API(auth, proxy=config.TwitterConfig.Proxy)

        places = api.geo_search(lat=lat, long=long, granularity="neighborhood")
        if len(places) == 0:
            return
        place_id = places[0].id
        tweets = api.search(q="place:%s" % place_id,
                            until=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                            count=100, result_type="recent")
        results = []
        for tweet in tweets:
            results.append({'id': tweet.id, 'text': tweet.text, 'name': tweet.user.name, 'uid': tweet.user.id,
                            'date': tweet.created_at, 'place': tweet.place.name, 'senti': self.get_senti(tweet.text)})
        return results

    def get_senti(self, text):
        senti = TextBlob(text)
        polar = senti.sentiment.polarity
        # print('sentiment result-----',polar)
        return polar
