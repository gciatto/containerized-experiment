ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}
RUN mkdir -p /experiment
VOLUME "/data"
ENV OUTPUT_DIR=/data
WORKDIR /experiment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY * /experiment/
ENV OWNER=1000:1000
CMD python experiment.py | tee ${OUTPUT_DIR}/output.log && \
    chown -R ${OWNER} ${OUTPUT_DIR}
