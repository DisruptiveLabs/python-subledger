# -*- coding: utf-8 -*-
"""\

Data
ORG
Bitmymoney
id: ivMaXfSHBQ9hBq5igz5nU1



"""
from models import Organization, Book, Account, JournalEntry


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    (id_, secret) = file('subledger.secret').read().strip().split()
    Organization.authenticate(id_, secret)

    org_id = 'ivMaXfSHBQ9hBq5igz5nU1'

    #o = Organization.from_id(org_id)
    #print o

    # Test if we can skip loading the Org first
    from base import Dummy

    o = Dummy()
    o._id = org_id
    #b = Book(a._id, 'XBT')
    #b.save()

    #b = Book.from_id(u'nFCZ2CIDfIkaY1f6b7bBG4', a._id)
    tmp = set()
    for b in Book.all(o, state='archived'):
        print b.description
        print b.is_active
    for b in Book.all(o, state='active'):
        print b.description
        print b.is_active
