FROM python:3.11-slim

WORKDIR /app

COPY src/penroselamarck/orchestrator/python-requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Placeholder command until scheduler/runtime wiring is added.
CMD ["python", "-m", "penroselamarck.orchestrator"]
