FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

RUN apt-get update \
    && apt-get install -y gcc mariadb-server libmariadb-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./app /app 
COPY app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt
