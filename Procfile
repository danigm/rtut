release: sh -c 'cd rtutpr && python manage.py migrate'
web: sh -c 'cd rtutpr && gunicorn rtutpr.wsgi --log-file -'
