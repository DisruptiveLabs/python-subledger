# -*- coding: utf-8 -*-
"""\

Data
ORG
Bitmymoney
id: ivMaXfSHBQ9hBq5igz5nU1



"""
import requests
import json

HTTP_GET = 0
HTTP_POST = 1
HTTP_PATCH = 2


class Access(object):
    """Client access to your Subledger account
    """
    def __init__(self, key_id, secret):
        """ """
        self._key_id = key_id
        self._secret = secret
        self.api_url = "https://api.subledger.com/v1/"
    
    def _json_request(self, path, method=HTTP_GET, data=None):
        """ """
        url = self.api_url + path
        auth=(self._key_id, self._secret)
        
        # TODO: rewrite without if / elif
        if method == HTTP_GET:
            # TODO: pass data as query string
            r = requests.get(url, auth=auth)
        elif method == HTTP_POST:
            r = requests.post(url, data=data, auth=auth)
        elif method == HTTP_PATCH:
            r = requests.patch(url, data=data, auth=auth)
        # TODO: Error handling
        if r.status_code == 200:
            return r.json()
        else:
            raise ValueError(r.status_code, r.text)


class AccessMixin(object):
    """Provide access to a Subledger object 
    
    Before using the Subledger classes, instantiate an Access object
    >>> a = Access(key_id, secret)
    >>> AccessMixin.api = a
    
    >>> o = Organization('Belastingdienst')
    >>> o.save()
    
    Organization will be saved to our subledger book.
    """
    api = None


class Organization(AccessMixin):
    """ """
    def __init__(self, description, reference=None, id_=None):
        """ """
        self.description = description
        self.reference = reference
        # To be determined by Subledger
        self._id = id_
        self._version = None
        
    def save(self):
        """Write organization to Subledger 
        
        POST on new instance
        UPDATE when info has changed
        """
        data = {'description': self.description,
                'reference': self.reference,
                'version': self._version+1}
        _old = self._id
        if self._id:
            path = u'orgs/%s' % self._id
            method = HTTP_PATCH
        else:
            path = u'orgs/'
            method = HTTP_POST
        # TODO: Support archived org
        result = self.api._json_request(path, method, data)['active_org']
        # Store on self
        self._id = result['id']
        self._version = result['version']
        # Return True is it was created
        return _old is None
    
    @classmethod
    def from_id(cls, id_):
        """ """
        # Load Org from Subledger
        path = u'orgs/%s' % id_
        result =  cls.api._json_request(path, HTTP_GET)['active_org']
        
        # Create instance
        self = cls(result['description'], result['reference'])
        self._id = result['id']
        self._version = result['version']
        return self
    
    def __unicode__(self):
        return unicode(self.__dict__)
    

if __name__ == "__main__":
    (id_, secret) = file('subledger.secret').read().strip().split()
    AccessMixin.api = Access(id_, secret)
    #orgs = Orgs(api)
    #print orgs.get('ivMaXfSHBQ9hBq5igz5nU1')
    
    org_id = 'ivMaXfSHBQ9hBq5igz5nU1'
    
    a = Organization.from_id(org_id)
    print unicode(a)
    
    a.description = u'Belastingdienst'
    a.save()
    print unicode(a)
    
