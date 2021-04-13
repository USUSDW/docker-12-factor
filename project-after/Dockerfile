FROM python:3.8-slim-buster

WORKDIR /code

RUN pip install pipenv

COPY Pipfile Pipfile.lock /code/

RUN pipenv install --system

ENV port=5000

COPY . /code/

CMD ["flask", "run", "--no-reload", "--host", "0.0.0.0", "--port", "5000"]