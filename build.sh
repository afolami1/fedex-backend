#!/bin/bash

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User=get_user_model(); u,created=User.objects.get_or_create(username=os.environ['DJANGO_SUPERUSER_USERNAME'], defaults={'email':os.environ.get('DJANGO_SUPERUSER_EMAIL','')}); u.email=os.environ.get('DJANGO_SUPERUSER_EMAIL',''); u.is_staff=True; u.is_superuser=True; u.set_password(os.environ['DJANGO_SUPERUSER_PASSWORD']); u.save(); print('ADMIN ACCOUNT READY:',u.username)"
