run:
	python3 manage.py runserver 8000

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

daemon:
	celery -A config multi start worker1 \
    --pidfile="$HOME/run/celery/%n.pid" \
    --logfile="$HOME/log/celery/%n%I.log"

celery:
	celery -A config worker -l info