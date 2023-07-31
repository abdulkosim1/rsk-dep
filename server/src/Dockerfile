FROM python:3.10.9


WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev \
    libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales vim postgresql-client-13

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

COPY ./requirements.txt .
RUN python -m pip install --no-cache-dir --disable-pip-version-check --requirement requirements.txt

COPY . .

RUN mkdir -p /db/backups/
EXPOSE 8000
# RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@admin.com', '1')" | python manage.py shell
# CMD ["gunicorn","-b","0.0.0.0:8000","config.wsgi:application"]



