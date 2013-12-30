python-subledger
================

Python implementation of the Subledger.com API for double entry accounting

Documentation and API endpoint: https://api.subledger.com/

### Beware ###
This library is experimental and unfinished. Do not rely on it (yet).

Feel free to suggest code changes or features!

The base for working with Subledger is an Organization. You can get yourself an 
identity (user) with Subledger. With this identity and an API key, you can 
create an Organization. The Organization will house accounting Books and journal 
entries.

Implemented:
* Organization
* Book
* Account

Todo:
* JournalEntry
* Category
* Report
* ReportRenderings (nice to have)

Will not do:
* Identity (nice to have)

## Usage ##

    from subledger import Book, Organization
    
    # Authenticate with your Subledger credentials
    Book.authenticate(api_key, api_secret)
    
    # Use your organization to browse the books and accounts
    org = Organization.from_id('<your org ID>')
    for book in Book.all(org):
        print book
    
    # Create a new book and archive it immediately
    book = Book(org, 'USD')
    book.save()
    print len(list(Book.all(org))), 'active books'
    print len(list(Book.all(org, state='archived'))), 'archived books'

    book.archive()
    print len(list(Book.all(org))), 'active books'
    print len(list(Book.all(org, state='archived'))), 'archived books'
    

## Class pattern ##

### SubledgerBase ###
All models derive from SubledgerBase
#### .authenticate(key_id, secret)
Register your API key credentials to get access to the Subledger API.

#### .from_id(id_)
Create the instance by loading the data from Subledger. 

#### .from_dict(dict)
Create the instance from the given dict without requests to Subledger. 

#### .save()
Write the values to Subledger. 

It will not save data recursively. For example;
    book.save()
will **not** save changes made to book.organization

### Organization ###
#### .from_id(org_id)

### Book ###
#### .from_id(book_id, org_id)
#### .organization
The Organization object this Book belongs to.

### Account ###
#### .from_id(account_id, org_id, book_id)
#### .book
The Book object this Account belongs to.

