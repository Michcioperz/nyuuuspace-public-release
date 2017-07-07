## Steps that should (at least in theory) get this running

- download all this code somewhere
- remember to use Python in version at least 3.5
- create a virtualenv and activate it unless you know how to get by without it
- `pip install -r requirements.txt`
- make sure you understand the assumptions the code makes or alter the code
- `python3 manage.py migrate`
- `python3 manage.py createsuperuser` for yourself
- use `python3 manage.py shell` to add some pronouns, or at the very least, a pronoun with reflexive form "themself" – it's more important than you might imagine
- `python3 manage.py collectstatic`
- set up a cron job to run `python3 manage.py runcrons`
- start it up with something like gunicorn, perhaps

Additional steps are necessary to get "there is new content, please refresh page" notifications

- go into pubsub directory
- `npm install`
- set IO\_SOCKET to a file that should be a Unix socket used to communicate with the notifications server
- `nodejs index.js`

## Assumptions made by the system as it is right now in this source code

- it is run on nyuuu.space domain (this can be changed in settings.py, but you should also look for occurences of it in nyuuustead/views.py and in various templates (I'm really sorry))
- it is configured in the Django way to send email (set EMAIL\_HOST, EMAIL\_PORT, EMAIL\_HOST\_USER, EMAIL\_HOST_PASSWORD in settings.py according to [Django docs](https://docs.djangoproject.com/en/1.11/topics/email/#smtp-backend))
- it is given the cookie-and-what-not secret key via environment variable SECRET\_KEY
- it has access to a PostgreSQL database nyuuu via a user nyuuu which it can access without password on localhost
- it can put static files in static directory in current user's home directory, or if home is not set, in static directory right next to manage.py
- static files will be served by nginx or apache or whatever
- it has access to Redis without password on localhost and it will use either 0th database on it or the one specified by REDIS\_DB environment variable
- admin panel should be available at /adverb/ URL
- daily notifications should be sent at 13:37
- the nicest colours are the ones specified in nyuuustead/models.py in BEST\_COLOURS
- actually my contact info is in templates/registration/activate.html, please don't

## What could be done better

- a lot
- I'm too tired of this project to think logically now
