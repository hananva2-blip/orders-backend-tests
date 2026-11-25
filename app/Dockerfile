FROM python:3.12-slim
RUN pip install --no-cache-dir fastapi==0.165.0 uvicorn==0.54.0 "psycopg[binary]==3.3.9" pyjwt==2.15.1 \
    pydantic==2.14.4 email-validator==2.4.0
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
