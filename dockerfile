FROM python:3.9.13-slim-buster

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . ./

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD python3 app.py