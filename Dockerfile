FROM python:3.12-slim

WORKDIR /service

COPY . .
RUN pip install --no-cache-dir ".[frontend]"

# Build the document index and seed the database into the image.
RUN python -m assistant.ingest

EXPOSE 8000 8501
CMD ["uvicorn", "assistant.api:app", "--host", "0.0.0.0", "--port", "8000"]
