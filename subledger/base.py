"""\
Under the hood base classes and functionality

TODO: use logging module and log http request under debug level
"""
import requests


class Dummy:
    """Imitate Subledger instances without http requests to Subledger """
    pass


def memoize(func):
    """ Memorize instances by id, passed as first args parameter
    
    Apply this decorator on the from_id class method
    Note that this decorator ignores **kwargs
    """

    def memoizer(cls, id_, *args, **kwargs):
        if id_ in cls._instance_index:
            return cls._instance_index[id_]
        else:
            instance = func(cls, id_, *args, **kwargs)
            cls._instance_index[id_] = instance
        return instance
    return memoizer


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


class SubledgerBase(object):
    """Provide access to a Subledger object 
    
    Before using the Subledger classes, instantiate an Access object
    >>> a = Access(key_id, secret)
    >>> SubledgerBase.api = a
    
    Example:
    >>> o = Organization('Belastingdienst')
    >>> o.save()
    
    Organization will be saved to our subledger book.
    """
    api = None
    # Object ID's are globally unique, so we can index these
    _instance_index = {}
    
    def __init__(self, description, reference=None):
        # Attributes available on all 
        self.description = description
        self.reference = reference
        # Values to be determined by Subledger
        self._id = None
        self._version = None
    
    @classmethod
    def authenticate(cls, key_id, secret):
        SubledgerBase.api = Access(key_id, secret)
    
    #def archive(self):
        ## TODO: finisch this
        #path = self.api
        
    def _save(self, path, data):
        """Write data to Subledger 
        
        POST on new instance
        UPDATE when info has changed
        """
        # Read 
        data.update({'description': self.description,
                     'reference': self.reference,})
        _old = self._id
        if self._id:
            data['version'] = self._version + 1
            # Update existing
            result = self.api.patch_json(path, data)
        else:
            # Create new instance
            result = self.api.post_json(path, data)
        
        type_ = result.keys()[0]
        if type_ not in self.types:
            msg = u'Subledger type `%s` not in types %s'
            raise ValueError(msg % (type_, self.types))
        # Store metadata on self
        self._id = result[type_]['id']
        self._version = result[type_]['version']
        # Return True is it was created, False on update
        return _old is None

    @classmethod
    def from_id(cls):
        """Load instance from Subledger by id """
        raise NotImplementedError('Each class should implement from_id')

    @classmethod
    def from_dict(cls):
        """Create instance from values without contacting Subledger """
        raise NotImplementedError('Each class should implement from_dict')

    def __unicode__(self):
        return unicode(self.__dict__)