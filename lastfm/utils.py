# -*- coding: utf-8 -*-
import hashlib, json, requests
from lastify.settings import LASTFM

## LASTFM ##
class LastFMUtil(object):

    def __init__(self, token=None):
        self.token = token

    def getAPISig(self, method, secret=LASTFM['API_SECRET'], API_KEY=LASTFM['API_KEY']):
        signature = hashlib.md5("api_key{}method{}token{}{}".format(API_KEY, method, self.token, secret)).hexdigest()
        return signature

    def connectUser(self):
        if self.token is None:
            return False

        api_sig = self.getAPISig(method="auth.getSession")
        callback_url = "http://ws.audioscrobbler.com/2.0/?method=auth.getSession&api_key={}&token={}&api_sig={}&format=json".format(LASTFM['API_KEY'], self.token, api_sig)

        try:
            request = requests.get(callback_url)
        except:
            return False

        response = json.loads(request.content)

        return response["session"]["name"]

    def makeAPICall(self, method, username,data=""):
        url = "http://ws.audioscrobbler.com/2.0/?method={}&user={}&api_key={}&format=json{}".format(method, username, LASTFM['API_KEY'], data)

        try:
            request = requests.get(url)
        except:
            return False
        
        return json.loads(request.content)