# Back-end Development Capstone

Django band website integrating the Flask Pictures API on IBM Code Engine and the Flask/MongoDB Songs API on OpenShift. The main application runs in Kubernetes.

## Features

- Home, songs with lyric dialogs, and photo gallery.
- Signup, authentication, concert list and validated RSVP updates.
- Django administration for concerts and attendance.
- Environment-configured API endpoints, timeouts and service error handling.

## Local development

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations concert
python manage.py migrate
python manage.py test concert -v 2
python manage.py runserver 0.0.0.0:8000
```

Start the Songs service on port 5001 with a reachable MongoDB and Pictures on port 5002, or set SONGS_SERVICE_URL and PICTURES_SERVICE_URL to their deployed /song and /picture endpoints.

## Container and Kubernetes

```sh
docker build -t us.icr.io/$SN_ICR_NAMESPACE/djangoserver:1 .
docker run --rm --entrypoint python us.icr.io/$SN_ICR_NAMESPACE/djangoserver:1 manage.py test concert -v 2
docker push us.icr.io/$SN_ICR_NAMESPACE/djangoserver:1
kubectl apply -f deployment.yml
kubectl rollout status deployment/djangoserver
kubectl port-forward deployment/djangoserver 8001:8000
```

The entrypoint applies migrations and collects static assets. Create an administrator with `python manage.py createsuperuser`; no shared administrator password is included. The lab SQLite database is ephemeral across pod recreation.

## Configuration

DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS and DJANGO_CSRF_TRUSTED_ORIGINS configure Django. The supplied lab defaults support the Skills Network proxy. For production, set a persistent secret, disable debug, use a production WSGI server and persistent database/storage.

## Validation

Eleven Django tests cover signup, hashed passwords, duplicate usernames, login/logout, protected concert pages, RSVP validation and updates, missing concerts, and service failures. Tests passed both in the lab and the Python 3.9 container.

Related repositories: [Pictures](https://github.com/Akua49/Back-End-Development-Pictures) and [Songs](https://github.com/Akua49/Back-End-Development-Songs).

Based on the IBM Skills Network course template, under Apache-2.0.
