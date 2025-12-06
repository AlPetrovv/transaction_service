FROM python:3.12.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN useradd -m app
RUN apt update && apt install -y python3-dev gettext gdal-bin libgdal-dev python3-gdal
RUN pip install --upgrade pip


WORKDIR /home/app/transaction_service

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY transaction_service .

RUN chown -R app:app /home/app/

USER app
