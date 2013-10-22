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
        self.api_url = "https://api.subledger.com/v1"
    
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
        if r.status_code in (200, 201):
            return r.json()
        else:
            raise ValueError(r.status_code, r.text)


class StorageMixin(object):
    """Provide access to a Subledger object 
    
    Before using the Subledger classes, instantiate an Access object
    >>> a = Access(key_id, secret)
    >>> StorageMixin.api = a
    
    Example:
    >>> o = Organization('Belastingdienst')
    >>> o.save()
    
    Organization will be saved to our subledger book.
    """
    api = None
    
    def __init__(self):
        # Values to be determined by Subledger
        self._id = None
        self._version = None
        
    def _save(self, path, data):
        """Write data to Subledger 
        
        POST on new instance
        UPDATE when info has changed
        """
        _old = self._id
        if self._id:
            method = HTTP_PATCH
            data['version'] = self._version + 1
        else:
            # Create new instance
            method = HTTP_POST
        
        result = self.api._json_request(path, method, data)
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
    def from_id(cls, *args):
        raise NotImplementedError('Each class should implement from_id')

    def __unicode__(self):
        return unicode(self.__dict__)


class Organization(StorageMixin):
    """Subledger Organization object
    
    This is the identity for the owner of one or more accounting books. For 
    example, the organization "Bitmymoney.com" can have 2 accounting Books:
    EUR and XBT. For transactions in euro and bitcoin respectively.
    """
    path = '/orgs'
    types = ('active_org', 'archived_org')
    
    def __init__(self, description, reference=None):
        """ """
        super(Organization, self).__init__()
        # Organization specific fields
        self.description = description
        self.reference = reference
    
    def save(self):
        """Store Organization instance in Subledger 
        
        The `id` will be created by Subledger for a new Organization.
        
        `description` and `reference` will taken from the instance.
        `version` will be incremented automatically.
        """
        path = self.path + '/%s' % self._id or ''
        data = {'description': self.description,
                'reference': self.reference,}
        return self._save(path, data)

    @classmethod
    def from_id(cls, id_): #, org_id=None, book_id=None, *args, **kwargs):
        """Read object with the given id from Subledger
        
        Most objects need additional id's to identify the resource, these will 
        be used to build the ReST path.
        """
        # Build path
        path = '%s/%s' % (cls.path, id_)
        result =  cls.api._json_request(path, HTTP_GET)
        data = result[result.keys()[0]]
        # Create instance
        self = cls(data['description'], data.get('reference'))
        self._id = data['id']
        self._version = data['version']
        return self


class Book(StorageMixin):
    """Subledger Book of accounts
    
    This is the accounting book than can be used for a single asset.
    """
    path = '/orgs/%(org_id)s/books/%(book_id)s'
    types = ('active_book', 'archived_book')
    
    def __init__(self, org_id, description, reference=None):
        """Create an accounting book for the given Organization.
        
        You cannot change
        """
        super(Book, self).__init__()
        # Book specific fields
        self._org_id = org_id
        self.description = description
        self.reference = reference
    
    def save(self):
        """Store Book instance in Subledger 
        
        The `id` will be created by Subledger for a new Organization.
        
        `description` and `reference` will taken from the instance.
        `version` will be incremented automatically.
        """
        path = self.path % {'org_id': self._org_id,
                             'book_id': self._id or ''}
        data = {'description': self.description,
                'reference': self.reference,}
        return self._save(path, data)
    

    @classmethod
    def from_id(cls, id_,org_id):
        """Read Book with the given id and org_id from Subledger
        
        A Book needs an Organization id to identify the resource. It will 
        be used to build the ReST path.
        """
        # Build path
        path = cls.path % {'org_id': org_id,
                           'book_id': id_}
        result =  cls.api._json_request(path, HTTP_GET)
        data = result[result.keys()[0]]
        # Create instance
        self = cls(data['org'], data['description'], data.get('reference'))
        self._id = data['id']
        self._version = data['version']
        return self


if __name__ == "__main__":
    (id_, secret) = file('subledger.secret').read().strip().split()
    StorageMixin.api = Access(id_, secret)
    
    org_id = 'ivMaXfSHBQ9hBq5igz5nU1'
    
    a = Organization.from_id(org_id)
    print unicode(a)
    #a.description = u'Belastingdienst'
    #a.save()
    #print unicode(a)
    
    #b = Book(a._id, 'XBT')
    #b.save()
    
    b = Book.from_id(u'nFCZ2CIDfIkaY1f6b7bBG4', a._id)
    print unicode(b)
    
