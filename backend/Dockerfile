FROM python:3.9.19-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/

COPY requirements.txt /app/

RUN pip install -r requirements.txt

ADD . /app/

CMD python manage.py migrate \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'anufrievmxm@gmail.com', 'admin')" \
    && python manage.py collectstatic --no-input \
    && python manage.py initialize_db \
    && echo y | python manage.py search_index --rebuild \
    && gunicorn backend.wsgi:application --bind 0.0.0.0:8000