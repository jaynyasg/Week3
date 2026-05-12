FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY agentforge /app/agentforge
COPY evals/cases /app/evals/cases
COPY evals/goldens /app/evals/goldens
COPY README.md ARCHITECTURE.md THREAT_MODEL.md USERS.md AI-COST-ANALYSIS.md /app/

RUN useradd --create-home --system --uid 10001 appuser \
    && mkdir -p /app/evals/results /app/evals/reports /app/evals/regression \
    && chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV AGENTFORGE_ARTIFACT_DIR=/app/evals

EXPOSE 8080

CMD ["uvicorn", "agentforge.http.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
