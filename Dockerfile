# Based on https://softwarejourneyman.com/docker-python-install-wheels.html

ARG BUILD_FROM

#########################################
# Image WITH C compiler, building wheels for next stage
FROM ${BUILD_FROM} as bigimage

ENV LANG C.UTF-8
ENV REST_SERVER_VERSION 0.9.7

# install the C compiler
RUN apk add --no-cache jq gcc musl-dev libffi-dev openssl-dev

# instead of installing, create a wheel
RUN pip wheel --wheel-dir=/root/wheels xbox-smartglass-rest==${REST_SERVER_VERSION}

#########################################
# Image WITHOUT C compiler, installing the component from wheel
FROM ${BUILD_FROM} as smallimage

RUN apk add --no-cache openssl

COPY --from=bigimage /root/wheels /root/wheels

# Ignore the Python package index
# and look for archives in
# /root/wheels directory
RUN pip install \
      --no-index \
      --find-links=/root/wheels \
      xbox-smartglass-rest

CMD [ "xbox-rest-server" ]
