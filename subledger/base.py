"""\
Under the hood base classes and functionality

TODO: use logging module and log http request under debug level
"""
import logging
import json

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
            if cls is not type(cls._instance_index[id_]):
                raise TypeError('Instance with ID does not match class')
            return cls._instance_index[id_]
        else:
            instance = func(cls, id_, *args, **kwargs)
            cls._instance_index[id_] = instance
        return instance

    return memoizer


def memoize_from_dict(func):
    """ Memorize instances by id, passed in a dictionary
    
    Apply this decorator on the from_dict class method
    """

    def memoizer(cls, dictionary):
        id_ = dictionary['id']
        if id_ in cls._instance_index:
            # Ignore other values in dictionary when 'id' is present
            if cls is not type(cls._instance_index[id_]):
                raise TypeError('Instance with ID does not match class')
            return cls._instance_index[id_]
        else:
            instance = func(cls, dictionary)
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

    def create_new_identity(self, email, description, reference=None):
        logging.debug('Access.create_identity')
        logging.debug('email: %s', email)
        logging.debug('description: %s', email)
        logging.debug('reference: %s', email)
        data = {'email': email, 'description': description, 'reference': reference}
        path = '/identities'
        result = self.post_json(path=path, data=data)
        logging.debug('result: %s', result)
        self._key_id = result['active_key']['id']
        self._secret = result['active_key']['secret']
        return (self._key_id, self._secret)


    def get_json(self, path, data=None):
        return self._json_request(requests.get, path, params=data)

    def post_json(self, path, data):
        logging.debug('POST: %s' % (data,))
        json_data = json.dumps(data)
        return self._json_request(requests.post, path, data=json_data)

    def patch_json(self, path, data):
        logging.debug('PATCH: %s' % (data,))
        json_data = json.dumps(data)
        return self._json_request(requests.patch, path, data=json_data)

    def _json_request(self, req_func, path, **kwargs):
        """ """
        url = self.api_url + path
        auth = (self._key_id, self._secret)
        logging.info("%s (API_KEY: %s)" % (url, self._key_id))
        r = req_func(url, auth=auth, **kwargs)
        # TODO: Error handling
        if r.status_code in (200, 201, 202):
            return r.json()
        else:
            raise ValueError(r.status_code, r.text)


class SubledgerBase(object):
    """Base class for shared functionality of Subledger classes
    """
    _api = None
    _path = ''
    # Object ID's are globally unique, so we can index these
    _instance_index = {}

    def __init__(self, description, reference=None):
        # Attributes available on all 
        self.description = description
        self.reference = reference
        # Values to be determined by Subledger
        self._id = None
        self._version = None
        self._type = 'active'

    @classmethod
    def authenticate(cls, key_id, secret):
        # TODO: refactor
        SubledgerBase._api = Access(key_id, secret)

    def archive(self):
        """Archive this instance in Subledger. 
        
        Can be called on any instance of Organization, Book,
        Account, JournalEntry, Line, Category, Report
        """
        path = self._path % self.__dict__
        path += "/archive"
        result = self._api.post_json(path, {})
        # Remember the type for its state
        self._set_type(result.keys()[0])

    def activate(self):
        """Activate this instance in Subledger. 
        
        Can be called on any instance of Organization, Book,
        Account, JournalEntry, Line, Category, Report
        """
        path = self._path % self.__dict__
        path += "/activate"
        result = self._api.post_json(path, {})
        # Remember the type for its state
        self._set_type(result.keys()[0])

    @property
    def is_active(self):
        # TODO: Think about behavior with unsaved objects: True, False or None
        return self._type.startswith('active')

    def save(self):
        """Write data to Subledger 
        
        POST on new instance
        UPDATE when info has changed
        """
        # Build path
        data = self.__dict__.copy()
        data['_id'] = self._id or ''
        path = self._path % data
        path = path.rstrip('/')  # a trailing slash led to UNAUTHORIZED errors
        # Pop private keys
        for k in data.keys():
            if k.startswith('_'):
                del data[k]
        old_id = self._id
        if self._id:
            data['version'] = self._version + 1
            # Update existing
            result = self._api.patch_json(path, data)
        else:
            # Create new instance
            result = self._api.post_json(path, data)

        type_ = result.keys()[0]
        self._set_type(type_)
        # Store metadata on self
        self._id = result[type_]['id']
        self._version = result[type_]['version']
        # Index object for fast retrieval (and guarantee single occurance)
        SubledgerBase._instance_index[self._id] = self
        # Return True if it was created, False on update
        return self._id != old_id

    def _set_type(self, type_):
        if type_ in self._types:
            self._type = type_
        else:
            msg = u'Subledger type `%s` not in types %s'
            raise ValueError(msg % (type_, self._types))

    @classmethod
    def from_id(cls):
        """Load instance from Subledger by id """
        raise NotImplementedError('Each class should implement from_id')

    @classmethod
    def _from_dict(cls):
        """Create instance from values without contacting Subledger 
        
        This is a helper function not intended to be used on its own.
        """
        raise NotImplementedError('Each class should implement from_dict')

    def __unicode__(self):
        return unicode(self.__dict__)