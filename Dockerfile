FROM python:3.6-alpine

WORKDIR /worker/code

COPY scripts ./scripts
COPY requirements.txt ./

RUN \
    apk add --update --no-cache bash \
  && \
    /bin/bash scripts/build.sh \
  && \
    pip install -r requirements.txt \
  && \
    apk del .build-dependencies \
  && \
    rm -rf /var/cache/apk/* \
  && \
    addgroup -g 1001 -S workers \
  && \
    adduser -h /worker -S -s /bin/bash -G workers -D -H -u 1001 worker \
  && \
    chown worker:workers -R /worker

COPY monitor.py ./monitor.py
COPY run.sh ./run.sh

RUN chmod +x monitor.py && chmod +x run.sh

CMD /worker/code/run.sh
