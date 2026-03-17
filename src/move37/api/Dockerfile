FROM python:3.12-slim

WORKDIR /app

COPY src/move37/api/python-requirements.txt ./python-requirements.txt
RUN pip install --no-cache-dir -r python-requirements.txt

COPY src /app/src

ENV PYTHONPATH=/app/src
EXPOSE 8080

CMD ["uvicorn", "move37.api.server:app", "--host", "0.0.0.0", "--port", "8080"]
