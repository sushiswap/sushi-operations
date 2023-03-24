FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
  python3.10 \
  python3-pip

SHELL ["/bin/bash", "-c"]
WORKDIR /opt/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./src .

ENTRYPOINT ["python3", "main.py"]