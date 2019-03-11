FROM python:3.7-alpine
LABEL maintainer "Charlie Orford <email+docker@charlie.is>"

RUN mkdir /instance
COPY ./jwt /instance/jwt/
VOLUME /instance

RUN set -x ; \
    addgroup -g 1001 -S webapp ; \
    adduser -u 1001 -D -S -G webapp webapp && exit 0 ; exit 1

COPY --chown=webapp:webapp . /webapp/
WORKDIR /webapp

RUN pip install -r requirements.txt

USER webapp

ENV FLASK_ENV=production

EXPOSE 5000
ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:5000", "--log-level", "INFO", "manage:app" ]
