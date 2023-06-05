FROM python:3.9

USER root

RUN apt-get update \
    && apt-get install -y gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
COPY ./train /train
COPY train/requirements.txt /train/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --user -r /train/requirements.txt

ENTRYPOINT [ "python3", "/train/main.py" ]