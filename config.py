import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'Ap4lh1Lk2jI241kcjljwIjHL'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' }]

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sqlite_database.db')

# administrator list
ADMINS = ['sandeep.sidhu@rackspace.co.uk']

# pagination
TABLEROWS_PER_PAGE = 3
