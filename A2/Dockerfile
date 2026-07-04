FROM python:3.9-slim-bookworm

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY Rest_API.py ./
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libmariadb3 \
    libmariadb-dev
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "./Rest_API.py"]