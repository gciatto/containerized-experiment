ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}
RUN mkdir -p /experiment
VOLUME "/data"
ENV OUTPUT_DIR=/data
WORKDIR /experiment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY * /experiment/
CMD python experiment.py | tee ${OUTPUT_DIR}/output.log
