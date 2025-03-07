FROM python:3.13.2-slim-bookworm AS build

WORKDIR /app

COPY clean.py .
COPY config.py .
COPY parse.py .
COPY requirements.txt .
COPY scan.py .
COPY soapi.py . 
COPY upload.py . 

RUN pip install --no-cache-dir -r requirements.txt

FROM build AS run

CMD ["python", "soapi.py"]
