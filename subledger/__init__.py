# -*- coding: utf-8 -*-
"""\

Data
ORG
Bitmymoney
id: ivMaXfSHBQ9hBq5igz5nU1



"""

from models import Book, Organization


if __name__ == "__main__":
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
    for b in Book.all(o, state='active', action='starting'):
        print b
    
