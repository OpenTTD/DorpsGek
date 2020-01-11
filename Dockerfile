FROM python:3.7-slim

ARG BUILD_DATE=""
ARG BUILD_VERSION="dev"

LABEL maintainer="truebrain@openttd.org"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.build-date=${BUILD_DATE}
LABEL org.label-schema.version=${BUILD_VERSION}

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt \
        LICENSE \
        README.md \
        dorpsgek.ini \
        /code/
COPY dorpsgek /code/dorpsgek

RUN pip install -r requirements.txt

# Validate that what was installed was what was expected
RUN pip freeze 2>/dev/null > requirements.installed \
        && diff -u --strip-trailing-cr requirements.txt requirements.installed 1>&2 \
        || ( echo "!! ERROR !! requirements.txt defined different packages or versions for installation" \
                && exit 1 ) 1>&2

ENTRYPOINT ["python", "-m", "dorpsgek"]
CMD []
