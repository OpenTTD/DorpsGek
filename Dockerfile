FROM python:3.7-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt \
        LICENSE \
        README.md \
        .version \
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
