FROM python:3.8-slim

LABEL maintainer="Edgardo Peregrino"

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
