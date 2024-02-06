FROM python:3.11.1

ENV PYTHONDONTWRITEBYTECODE
ENV ENV
ENV POSTGRES_URL
ENV JWT_KEY
ENV JWT_ALGORITHM
ENV REDIS_HOST
ENV REDIS_PORT
ENV REDIS_PWD

WORKDIR /app

COPY /src /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]