FROM python:3.12-slim

WORKDIR /app

COPY src/move37/worker/python-requirements.txt ./python-requirements.txt
RUN pip install --no-cache-dir -r python-requirements.txt

COPY src /app/src

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "move37.worker.runner"]
