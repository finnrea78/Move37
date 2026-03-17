FROM python:3.12-slim

WORKDIR /app

COPY src/move37/rag/python-requirements.txt ./python-requirements.txt
RUN pip install --no-cache-dir -r python-requirements.txt

COPY src /app/src

ENV PYTHONPATH=/app/src
EXPOSE 8090

CMD ["uvicorn", "move37.rag.api:app", "--host", "0.0.0.0", "--port", "8090"]
