FROM python:3.10

WORKDIR /app

# Install system dependencies for MySQL client and netcat
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    libffi-dev \
    libssl-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --index-url https://phonepe.mycloudrepo.io/public/repositories/phonepe-pg-sdk-python \
    --extra-index-url https://pypi.org/simple phonepe_sdk
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project files
COPY . .

# Copy wait-for-db.sh and setup.sh
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

COPY setup.sh /setup.sh
RUN chmod +x /setup.sh

EXPOSE 8000

ENTRYPOINT ["/setup.sh"]
