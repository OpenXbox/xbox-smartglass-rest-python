FROM resin/armv7hf-python:3.6-slim

RUN [ "cross-build-start" ]
RUN apt-get update && apt-get install -y gcc libc-dev python3-dev libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*
RUN pip install gevent==1.2.2

COPY . .
RUN pip install -e ./

EXPOSE 5557/tcp

RUN [ "cross-build-end" ]
CMD [ "xbox-rest-server" ]
