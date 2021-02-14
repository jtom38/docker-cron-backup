FROM ubuntu:20.04

RUN apt update \
    && apt install curl tar -y python3 python3-pip\
    && python3 -m pip install requests \
    && mkdir /scripts /backup 

COPY ./scripts /scripts
RUN chmod +x /scripts/backup.py 
