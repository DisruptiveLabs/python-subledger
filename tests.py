# -*- coding: utf-8 -*-
"""\
Test the Subledger Python API functionality

Identity created for this purpose
{
  "active_identity": {
    "id": "tVlYHmPf35IncGiqfhMuT3",
    "email": "r.r.nederhoed@gmail.com",
    "description": "Identity for automated Unit testing",
    "version": 1
  },
  "active_key": {
    "id": "5AQT3d51VIZH6G778afB37",
    "identity": "tVlYHmPf35IncGiqfhMuT3",
    "secret": "ybLmLioCNSji8PsByWzxn2"
  }
}
"""
import unittest
import logging

logger = logging.getLogger()
logger.setLevel('DEBUG')

from subledger.base import Access
from subledger.models import Organization, Book

# Setup the test account
API_KEY = None
SECRET = None


class TestCreateAPIKey(unittest.TestCase):
    access = Access(key_id=None, secret=None)
    assert access._key_id is None
    assert access._secret is None
    key_id, secret = access.create_new_identity(email='r.r.nederhoed@gmail.com',
                                                description='Identity for automated Unit testing',
                                                reference='https://www.acme.com/')
    assert access._key_id is not None
    assert key_id == access._key_id
    assert access._secret is not None
    assert secret == access._secret
    # While we're at it, override the API_KEY and SECRET using this newly created identity if they're set to None
    if API_KEY is None or SECRET is None:
        global API_KEY, SECRET
        API_KEY = key_id
        SECRET = secret


class TestOrganization(unittest.TestCase):
    def setUp(self):
        # Setup access to Subledger
        Organization.authenticate(API_KEY, SECRET)
        self.company_name = 'ACME Inc.'
        self.reference = 'https://www.acme.com/'
        self.org = Organization(self.company_name, self.reference)

    def test_constructor(self):
        # Attribute values
        self.assertEqual(self.org.description, self.company_name)
        self.assertEqual(self.org.reference, self.reference)

    def test_new_or_not(self):
        # New company, not in Subledger
        self.assertEqual(self.org._id, None)
        new = self.org.save()
        self.assertEqual(new, True)
        new = self.org.save()
        self.assertEqual(new, False)


class TestOrganizationLoad(unittest.TestCase):
    def setUp(self):
        # Setup access to Subledger
        Organization.authenticate(API_KEY, SECRET)
        self.company_name = 'ACME Inc.'
        self.reference = 'https://www.acme.com/'
        self.org = Organization(self.company_name, self.reference)
        self.org.save()

    def test_from_id(self):
        retrieved = Organization.from_id(self.org._id)
        self.assertIs(retrieved, self.org)

    def test_from_dict_index(self):
        retrieved = Organization._from_dict({'id': self.org._id})
        # Identity
        self.assertIs(retrieved, self.org)

    def test_from_dict(self):
        org = Organization._from_dict(
            {'id': None,
             'version': self.org._version,
             'type': self.org._type,
             'description': self.company_name,
             'reference': self.reference})
        # Attribute values
        self.assertEqual(org.description, self.company_name)
        self.assertEqual(org.reference, self.reference)
        # Identity
        self.assertIsNot(org, self.org)


class TestOrganizationArchive(unittest.TestCase):
    def setUp(self):
        # Setup access to Subledger
        Organization.authenticate(API_KEY, SECRET)
        self.company_name = 'ACME Inc.'
        self.reference = 'https://www.acme.com/'
        self.org = Organization(self.company_name, self.reference)
        self.org.save()

    def test_active_by_default(self):
        self.assertEqual(self.org.is_active, True)

    def test_archive_and_activate(self):
        self.assertEqual(self.org.is_active, True)
        self.org.archive()  # Beware, this has immediate effect
        self.assertEqual(self.org.is_active, False)
        self.org.activate()  # Beware, this has immediate effect
        self.assertEqual(self.org.is_active, True)


class TestBook(unittest.TestCase):
    def setUp(self):
        # Setup access to Subledger
        Organization.authenticate(API_KEY, SECRET)
        self.org = Organization('ACME Inc.')
        self.org.save()
        self.book = Book(self.org, 'XBT')
        self.book.save()

    def test_from_id(self):
        retrieved = Book.from_id(self.book._id, self.org._id)
        self.assertIs(retrieved, self.book)

    def test_from_dict_index(self):
        data = {'id': self.book._id, 'org': self.org._id}
        logging.info(data)
        retrieved = Book._from_dict(data)
        # Identity
        self.assertIs(retrieved, self.book)

    def test_from_dict(self):
        book = Book._from_dict(
            {'id': None,
             'org': self.org._id,
             'version': self.book._version,
             'type': self.book._type,
             'description': 'EUR'})
        # Attribute values
        self.assertEqual(book.description, 'EUR')
        self.assertEqual(book.reference, None)
        # Identity
        self.assertIsNot(book, self.book)


if __name__ == '__main__':
    unittest.main()