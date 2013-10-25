# -*- coding: utf-8 -*-
"""\

Data
ORG
Bitmymoney
id: ivMaXfSHBQ9hBq5igz5nU1



"""
import requests
#import json

from models import SubledgerBase
from models import Book, Organization


class Access(object):
    """Client access to your Subledger account
    """
    def __init__(self, key_id, secret):
        """ """
        self._key_id = key_id
        self._secret = secret
        self.api_url = "https://api.subledger.com/v1"
    
    def get_json(self, path, data=None):
        return self._json_request(requests.get, path, params=data)
    
    def post_json(self, path, data):
        return self._json_request(requests.post, path, data=data)
    
    def patch_json(self, path, data):
        return self._json_request(requests.patch, path, data=data)
        
    def _json_request(self, req_func, path, **kwargs):
        """ """
        url = self.api_url + path
        auth=(self._key_id, self._secret)
        print 'REQ', url
        r = req_func(url, auth=auth, **kwargs)
        # TODO: Error handling
        if r.status_code in (200, 201):
            return r.json()
        else:
            raise ValueError(r.status_code, r.text)



if __name__ == "__main__":
    (id_, secret) = file('subledger.secret').read().strip().split()
    SubledgerBase.api = Access(id_, secret)
    
    org_id = 'ivMaXfSHBQ9hBq5igz5nU1'
    
    #o = Organization.from_id(org_id)
    #print o
    # Dummy
    from models import Dummy
    o = Dummy()
    o._id = org_id
    #b = Book(a._id, 'XBT')
    #b.save()
    
    #b = Book.from_id(u'nFCZ2CIDfIkaY1f6b7bBG4', a._id)
    for b in Book.all(o, state='active', action='starting'):
        print b
    
