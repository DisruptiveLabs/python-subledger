"""\
Subledger API accounting models


TODO: .archive() and .activate() on SubledgerBase

TODO: JournalEntry model
TODO: Category model
TODO: Report model

Nice to haves
DONE: store _org_id in Book
      use property to load the Org on lookup
      self._org_id = '8750282098'
      @property
      def organization(self):
          Read Org form cache or Subledger

DONE: let each object have Singleton behaviour based on it's ID. This way \
      changes in one place, will be effective on all instances with the same \
      identity.
      
"""
from base import memoize
from base import Dummy, SubledgerBase


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
    
    @classmethod
    def from_dict(cls, data):
        """Instantiate a Organization from a Subledger representation 
        
        All data should be in the dictionary `data`
        This method will not query Subledger
        """
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
        
        You cannot change the organization the Book belongs to.
        """
        super(Book, self).__init__(description, reference)
        # Book specific fields
        self._org_id = org._id  # Rember the org_id
    
    @property
    def organization(self):
        """Return the organization that owns this Book """
        # Organization will return itself from cache or load from Subledger
        return Organization.from_id(self._org_id)
        
    def save(self):
        """Store Book instance in Subledger 
        
        The `id` will be created by Subledger for a new Book.
        
        `description` and `reference` will taken from the instance.
        `version` will be incremented automatically.
        """
        path = self.path % {'org_id': self._org._id,
                             'book_id': self._id or ''}
        return self._save(path, {})
    
    @classmethod
    def all(
        cls, organization, state='active',
        action='starting', id_=None, description=None, limit=None):
        """Iterate over all books for given organization """
        path = cls.path % {'org_id': organization._id, 'book_id': ''}
        data = {'state': state, 'action': action, 'id': id_,
                'description':description, 'limit': limit}
        result = cls.api.get_json(path, data)
        for v in result['%s_books' % state]:
            yield cls.from_dict(v)
    
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
        # Emulate Org object
        org = Dummy()
        org._id = data['org']
        # Create instance
        self = cls(org, data['description'], data.get('reference'))
        self._id = data['id']
        self._version = data['version']
        return self
    
    def __repr__(self):
        data = self.__dict__.copy()
        data['organization'] = Organization.from_id(self._org_id)
        return "Book(%(organization)r, %(description)s) %(_id)s" % data


class Account(SubledgerBase):
    """Subledger Account within a Book of accounts
    
    This is the accounting book than can be used for a single asset.
    """
    path = '/orgs/%(org_id)s/books/%(book_id)s/%(account_id)s'
    types = ('active_account', 'archived_account')
    
    def __init__(
        self, book, description, normal_balance='credit', reference=None):
        """Create an accounting book for the given Organization.
        
        `book` should be passed as an instance of Book
        """
        super(Account, self).__init__(description, reference)
        # Account specific fields
        self._org_id = book.org_id
        self._book_id = book._id
        # Debit or Credit account?
        self.normal_balance = normal_balance # 'debit' or 'credit'
    
    @property
    def book(self):
        """Return the Book that this account exists in """
        # Book will return itself from cache or load from Subledger
        return Book.from_id(self._book_id, self._org_id)
        
    def save(self):
        """Store Account instance in Subledger 
        
        The `id` will be created by Subledger for a new Account.
        
        `description` and `reference` will taken from the instance.
        `version` will be incremented automatically.
        """
        path = self.path % {'org_id': self.book._org._id,
                             'book_id': self.book._id,
                             'account_id': self._id or ''}
        # Book specific attributes
        data = {'normal_balance': self.normal_balance}
        return self._save(path, data)
    
    @classmethod
    def all(
        cls, book, state='active',
        action='starting', id_=None, description=None, limit=None):
        """Iterate over all accounts within given book """
        path = cls.path % {'org_id': book._org_id, 'book_id': book._id}
        data = {'state': state, 'action': action, 'id': id_,
                'description':description, 'limit': limit}
        result = cls.api.get_json(path, data)
        for v in result['%s_accounts' % state]:
            # Add org_id to the data, it is not returned by Subledger
            v['org'] = book._org_id
            yield cls.from_dict(v)
    
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
        # Add org_id to the data, it is not returned by Subledger
        data['org'] = org_id
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data):
        """Instantiate a Book from a Subledger representation 
        
        All data should be in the dictionary `data`
        This method will not query Subledger
        """
        # Emulate Book object without http requests
        book = Dummy()
        book._id = data['book']
        book._org_id = data['org']
        # Create Account instance
        self = cls(book, data['description'],
                   data['normal_balance'],
                   data.get('reference'))
        self._id = data['id']
        self._version = data['version']
        return self
    
    def __repr__(self):
        data = self.__dict__.copy()
        data['book'] = Book.from_id(self._book_id, self._org_id)
        signature = "Account(%(book)r, %(description)s, "\
            "%(normal_balance)s) %(_id)s"
        return signature % self.__dict__
