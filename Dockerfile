from python:3.12.9-alpine3.21

workdir /app


RUN apk update \
    && apk add --no-cache gcc musl-dev postgresql-dev python3-dev libffi-dev openssl-dev \
    && pip instsall --upgrade pip


COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./ ./

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

