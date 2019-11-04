FROM python:3.7-alpine

WORKDIR /crawler

RUN apk add --no-cache --virtual=build_dependencies musl-dev gcc python-dev make cmake g++ gfortran libxml2 libxml2-dev libxslt-dev && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip install numpy==1.16.2 && \
    pip install pandas==0.24.2 && \
    apk del build_dependencies && \
    apk add --no-cache libstdc++ && \
    rm -rf /var/cache/apk/*

RUN apk update \
    && apk add --no-cache --virtual bash \
    && apk add curl gcc g++ python-dev libxml2 libxml2-dev libxslt-dev\
    && apk add musl-dev \
    && apk add linux-headers \
    && apk add jpeg-dev \
    && apk add zlib-dev \
    && apk add mariadb-dev \
    && apk add libffi-dev \
    && rm -rf /var/cache/apk/*

COPY ./requirements.txt /crawler

RUN pip install -r requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS /crawler/config/takaval-f7405a48fd1a.json