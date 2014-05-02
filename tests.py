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
import datetime
import unittest
import logging

logger = logging.getLogger()
logger.setLevel('DEBUG')

from subledger.base import Access
from subledger.models import Organization, Book, Account, JournalEntry

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


class TestAccount(unittest.TestCase):
    def setUp(self):
        # Setup access to Subledger
        Organization.authenticate(API_KEY, SECRET)
        self.org = Organization('ACME Inc.')
        self.org.save()
        self.book = Book(self.org, 'USD')
        self.book.save()
        self.account = Account(book=self.book,
                               description='1210 Accounts Receivable',
                               normal_balance='debit')
        save_result = self.account.save()
        assert save_result == True


    def test_balance(self):
        at_datetime_utc = datetime.datetime.utcnow()
        balance_result = self.account.get_balance(at_datetime_utc=at_datetime_utc)
        self.assertIsNotNone(balance_result)
        self.assertIn('balance', balance_result)
        balance = balance_result['balance']

        self.assertIn('debit_value', balance)
        self.assertIn('type', balance['debit_value'])

        self.assertEqual(balance['debit_value']['type'], 'zero')
        self.assertIn('amount', balance['debit_value'])
        self.assertEqual(balance['debit_value']['amount'], '0')

        self.assertIn('credit_value', balance)
        self.assertIn('type', balance['credit_value'])
        self.assertEqual(balance['credit_value']['type'], 'zero')
        self.assertIn('amount', balance['credit_value'])
        self.assertEqual(balance['credit_value']['amount'], '0')

        self.assertIn('value', balance)
        self.assertIn('type', balance['value'])
        self.assertEqual(balance['value']['type'], 'zero')
        self.assertIn('amount', balance['value'])
        self.assertEqual(balance['value']['amount'], '0')


    def test_from_id(self):
        retrieved = Account.from_id(self.account._id, self.book._id)
        self.assertIs(retrieved, self.account)


    def test_from_dict_index(self):
        data = {'id': self.account._id, 'book': self.book._id}
        logging.info(data)
        retrieved = Account._from_dict(data)
        # Identity
        self.assertIs(retrieved, self.account)

    def test_from_dict(self):
        account = Account._from_dict(
            {'id': None,
             'book': self.book._id,
             'org': self.org._id,
             'version': self.account._version,
             'type': self.account._type,
             'normal_balance': self.account.normal_balance,
             'description': '1210 Accounts Receivable'})
        # Attribute values
        self.assertEqual(account.description, '1210 Accounts Receivable')
        self.assertEqual(account.reference, None)
        # Identity
        self.assertIsNot(account, self.account)


class TestJournalEntry(unittest.TestCase):
    def setUp(self):
        # Setup access to Subledger
        Organization.authenticate(API_KEY, SECRET)
        self.org = Organization('ACME Inc.')
        self.org.save()
        self.book = Book(self.org, 'USD')
        self.book.save()
        self.account_01 = Account(book=self.book,
                                  description='1210 Accounts Receivable',
                                  normal_balance='debit')
        save_result = self.account_01.save()
        assert save_result == True
        self.account_02 = Account(book=self.book,
                                  description='2110 Accounts Paypable',
                                  normal_balance='credit')
        save_result = self.account_02.save()
        assert save_result == True

        at_datetime_utc = datetime.datetime.utcnow()
        effective_at = at_datetime_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        lines = [
            {
                'account': self.account_01._id,
                'value': {
                    'type': 'debit',
                    'amount': '10.00'
                }
            },
            {
                'account': self.account_02._id,
                'value': {
                    'type': 'credit',
                    'amount': '10.00'
                }
            }
        ]
        self.journal_entry = JournalEntry(book=self.book,
                                          description='Recharge account',
                                          effective_at=effective_at,
                                          lines=lines,
                                          reference='http://acme.com/journal_entry/')
        save_result = self.journal_entry.save()
        self.assertTrue(save_result)


    def test_from_id(self):
        retrieved = JournalEntry.from_id(self.journal_entry._id, self.org._id, self.book._id)
        self.assertIs(retrieved, self.journal_entry)


if __name__ == '__main__':
    unittest.main()