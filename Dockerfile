FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies for Python ML/libs + Node.js build tooling.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    ca-certificates \
    git \
    libxml2-dev \
    libxslt1-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 for modern Vite builds.
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (backend + model + deployment runtime).
COPY backend/requirements.txt /app/backend/requirements.txt
COPY model/requirements.txt /app/model/requirements.txt
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /app/backend/requirements.txt \
    && pip install -r /app/model/requirements.txt \
    && pip install -r /app/requirements.txt \
    && pip install flask flask-cors gunicorn

# Build React frontend.
COPY frontend/package*.json /app/frontend/
RUN cd /app/frontend && npm install

COPY frontend /app/frontend
RUN cd /app/frontend && npm run build

# Copy application code after dependency layers.
COPY app.py /app/app.py
COPY model /app/model
COPY backend /app/backend
COPY detector /app/detector
COPY sample_data /app/sample_data

# Make built frontend assets available in common Flask static paths.
RUN mkdir -p /app/static /app/templates \
    && cp -r /app/frontend/dist/* /app/static/ \
    && if [ -f /app/frontend/dist/index.html ]; then cp /app/frontend/dist/index.html /app/templates/index.html; fi

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
