# worker/Dockerfile
FROM python:3.11-slim
WORKDIR /worker

# Install only what the worker needs
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir \
      redis==5.0.8 \
      rq==1.16.2 \
      SQLAlchemy==2.0.35 \
      psycopg[binary,pool]==3.2.1 \
      pandas==2.2.2 \
      numpy==1.26.4 \
      statsmodels==0.14.2 \
      boto3==1.34.156

COPY worker/worker.py /worker/worker.py
CMD ["python", "worker.py"]
