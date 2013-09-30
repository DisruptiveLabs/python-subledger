# -*- coding: utf-8 -*-
"""\

Data
ORG
Bitmymoney
id: ivMaXfSHBQ9hBq5igz5nU1
"""
import requests
import json


class Subledger(object):
    """Client access to your Subledger account
    """
    def __init__(self, key_id, secret):
        """ """
        self._key_id = key_id
        self._secret = secret
        self.api_url = "https://api.subledger.com/v1/"
    
    def _json_request(self, path, data=None):
        """ """
        url = self.api_url + path
        if data:
            r = requests.post(url, data=data, auth=(self._key_id, self._secret))
        else:
            r = requests.get(url, auth=(self._key_id, self._secret))
        # TODO: Error handling
        if r.status_code == 200:
            return r.json()
        else:
            raise ValueError(r.status_code, r.text)
    
class Orgs(object):
    """ """
    def __init__(self, api):
        self.api = api
    
    def new(self, description, reference=None):
        """POST new organization to Subledger """
        path = u'orgs/'
        data = {'description': description, 'reference': reference}
        return self.api._json_request(path, data)
        
    def get(self, id_):
        """ """
        path = u'orgs/%s' % id_
        return self.api._json_request(path)


class Organization(object):
    """ """
    def __init__(self, description, reference=None):
        """ """
        self.description = description
        self.reference = reference
        # Receive from Subledger
        self._id = None
        self._version = None
    
    @classmethod
    def from_id(cls, id_):
        """ """
        # Load Org from Subledger
        self = cls(description, reference)
        self._id = id_
        return self
    
    def __unicode__(self):
        return unicode(self.__dict__)

if __name__ == "__main__":
    (id_, secret) = file('subledger.secret').read().strip().split()
    api = Subledger(id_, secret)
    orgs = Orgs(api)
    print orgs.get('ivMaXfSHBQ9hBq5igz5nU1')
    
    a = Organization.from_id(1)
    print unicode(a)