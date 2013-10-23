"""\
Subledger API accounting models


Nice to haves
TODO: store _org_id in Book
      use property to load the Org on lookup
      self._org_id = '8750282098'
      @property
      def organization(self):
          Read Org form cache or Subledger

DONE: let each object have Singleton behaviour based on it's ID. This way \
      changes in one place, will be effective on all instances with the same \
      identity.
      
"""

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
        
    def archive(self):
        # TODO: finisch this
        path = self.api
        
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
        raise NotImplementedError('Each class should implement from_id')

    def __unicode__(self):
        return unicode(self.__dict__)


class Organization(SubledgerBase):
    """Subledger Organization object
    
    This is the identity for the owner of one or more accounting books. For 
    example, the organization "Bitmymoney.com" can have 2 accounting Books:
    EUR and XBT. For transactions in euro and bitcoin respectively.
    """
    path = '/orgs'
    types = ('active_org', 'archived_org')
    
    def save(self):
        """Store Organization instance in Subledger 
        
        The `id` will be created by Subledger for a new Organization.
        
        `description` and `reference` will taken from the instance.
        `version` will be incremented automatically.
        """
        path = self.path + '/%s' % self._id or ''
        return self._save(path, {})

    @classmethod
    @memoize
    def from_id(cls, id_): #, org_id=None, book_id=None, *args, **kwargs):
        """Read object with the given id from Subledger
        
        Most objects need additional id's to identify the resource, these will 
        be used to build the ReST path.
        """
        # Build path
        path = '%s/%s' % (cls.path, id_)
        result =  cls.api.get_json(path)
        data = result[result.keys()[0]]
        # Create instance
        self = cls(data['description'], data.get('reference'))
        self._id = data['id']
        self._version = data['version']
        return self
    
    def __repr__(self):
        return "Organization(%(description)s) %(_id)s" % self.__dict__


class Book(SubledgerBase):
    """Subledger Book of accounts
    
    This is the accounting book than can be used for a single asset.
    """
    path = '/orgs/%(org_id)s/books/%(book_id)s'
    types = ('active_book', 'archived_book')
    
    def __init__(self, org, description, reference=None):
        """Create an accounting book for the given Organization.
        
        You cannot change
        """
        super(Book, self).__init__(description, reference)
        # Book specific fields
        self._org = org
    
    @classmethod
    def active(cls, organization):
        """Return iterator over all active books """
        path = cls.path % {'org_id': organization._id, 'book_id': ''}
        data = {'state': 'active',
                'action': 'starting'}
        result = cls.api.get_json(path, data)
        for v in result['active_books']:
            yield cls.from_dict(v)
        
    def save(self):
        """Store Book instance in Subledger 
        
        The `id` will be created by Subledger for a new Organization.
        
        `description` and `reference` will taken from the instance.
        `version` will be incremented automatically.
        """
        path = self.path % {'org_id': self._org._id,
                             'book_id': self._id or ''}
        return self._save(path, {})
    
    @classmethod
    @memoize
    def from_id(cls, id_, org_id):
        """Read Book with the given id and org_id from Subledger
        
        A Book needs an Organization id to identify the resource. It will 
        be used to build the ReST path.
        """
        # Build path
        path = cls.path % {'org_id': org_id, 'book_id': id_}
        result =  cls.api.get_json(path)
        data = result[result.keys()[0]]
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data):
        """Instantiate a Book from a Subledger representation 
        
        All data should be in the dictionary `data`
        This method will not query Subledger
        """
        # Load related important info
        org = Organization.from_id(data['org'])
        # Create instance
        self = cls(org, data['description'], data.get('reference'))
        self._id = data['id']
        self._version = data['version']
        return self
    
    def __repr__(self):
        return "Book(%(_org)r, %(description)s) %(_id)s" % self.__dict__


class Account(SubledgerBase):
    """Subledger Account within a Book of accounts
    
    This is the accounting book than can be used for a single asset.
    """
    path = '/orgs/%(org_id)s/books/%(book_id)s/%(account_id)s'
    types = ('active_account', 'archived_account')
    
    def __init__(
        self, book, description, normal_balance='credit', reference=None):
        """Create an accounting book for the given Organization.
        """
        super(Account, self).__init__(description, reference)
        # Account specific fields
        self._book = book
        # Debit or Credit account?
        self.normal_balance = normal_balance
    
    @classmethod
    def active(cls, book):
        """Return iterator over all active books """
        path = cls.path % {'org_id': book._org._id, 'book_id': ''}
        data = {'state': 'active',
                'action': 'starting'}
        result = cls.api.get_json(path, data)
        for v in result['active_books']:
            yield cls.from_dict(v)
        
    def save(self):
        """Store Book instance in Subledger 
        
        The `id` will be created by Subledger for a new Organization.
        
        `description` and `reference` will taken from the instance.
        `version` will be incremented automatically.
        """
        path = self.path % {'org_id': self.book._org._id,
                             'book_id': self.book._id,
                             'account_id': self._id or ''}
        data = {'normal_balance': self.normal_balance}
        return self._save(path, data)
    
    @classmethod
    @memoize
    def from_id(cls, id_, org_id, book_id):
        """Read Account with the given id, org_id and book_id from Subledger
        
        An Account needs a Book and Organization id's to identify the resource.
        It will be used to build the ReST path to the Account resource.
        """
        # Build path
        path = cls.path % {'org_id': org_id,
                           'book_id': book_id,
                           'account_id': id_}
        result =  cls.api.get_json(path)
        data = result[result.keys()[0]]
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data):
        """Instantiate a Book from a Subledger representation 
        
        All data should be in the dictionary `data`
        This method will not query Subledger
        """
        # Load related important info
        book = Book.from_id(data['book'])
        # Create instance
        self = cls(book, data['description'],
                   data['normal_balance'],
                   data.get('reference'))
        self._id = data['id']
        self._version = data['version']
        return self
    
    def __repr__(self):
        signature = "Account(%(_org)r, %(_org)r, %(description)s, "\
            "%(normal_balance)s) %(_id)s"
        return signature % self.__dict__
