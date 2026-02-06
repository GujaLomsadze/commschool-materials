# MinIO Complete Setup Guide for Ubuntu

## Table of Contents
1. [Quick Start (Development)](#quick-start-development)
2. [Production Setup with Systemd](#production-setup-with-systemd)
3. [Python Examples](#python-examples)
4. [Common Use Cases](#common-use-cases)

---

## Quick Start (Development)

For testing and development:

```bash
# Download MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# Create data directory
mkdir -p ~/minio-data

# Start MinIO server
minio server ~/minio-data --console-address ":9001"
```

**Access:**
- API: http://localhost:9000
- Web Console: http://localhost:9001
- Default Login: `minioadmin` / `minioadmin`

Press `Ctrl+C` to stop the server.

---

## Production Setup with Systemd

### Step 1: Install MinIO Binary

```bash
# Download latest MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio

# Make it executable
chmod +x minio

# Move to system bin
sudo mv minio /usr/local/bin/

# Verify installation
minio --version
```

### Step 2: Create MinIO User and Directories

```bash
# Create dedicated user for MinIO (no login shell)
sudo useradd -r minio-user -s /sbin/nologin

# Create data directory
sudo mkdir -p /mnt/minio/data

# Set ownership
sudo chown -R minio-user:minio-user /mnt/minio
```

### Step 3: Create Environment Configuration

```bash
# Create environment file
sudo nano /etc/default/minio
```

Add the following content (change credentials!):

```bash
# MinIO local volumes
MINIO_VOLUMES="/mnt/minio/data"

# MinIO Root credentials
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=YourStrongPassword123!

# MinIO options
MINIO_OPTS="--console-address :9001"

# Optional: Set region
MINIO_REGION_NAME=us-east-1

# Optional: Enable/disable browser
MINIO_BROWSER=on

# Optional: Server URL (for reverse proxy)
# MINIO_SERVER_URL=https://minio.yourdomain.com
# MINIO_BROWSER_REDIRECT_URL=https://console.yourdomain.com
```

**Important:** Change `MINIO_ROOT_PASSWORD` to a strong password!

### Step 4: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/minio.service
```

Add the following content:

```ini
[Unit]
Description=MinIO Object Storage
Documentation=https://min.io/docs/minio/linux/index.html
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable=/usr/local/bin/minio

[Service]
Type=notify

WorkingDirectory=/usr/local

User=minio-user
Group=minio-user
ProtectProc=invisible

# Load environment variables from file
EnvironmentFile=-/etc/default/minio

# Validate environment variables
ExecStartPre=/bin/bash -c 'if [ -z "${MINIO_VOLUMES}" ]; then echo "MINIO_VOLUMES not set in /etc/default/minio"; exit 1; fi'

# Start MinIO server
ExecStart=/usr/local/bin/minio server $MINIO_OPTS $MINIO_VOLUMES

# Restart policy
Restart=always
RestartSec=5

# Resource limits
LimitNOFILE=65536
TasksMax=infinity

# Graceful shutdown
TimeoutStopSec=infinity
SendSIGKILL=no

[Install]
WantedBy=multi-user.target
```

### Step 5: Set Permissions

```bash
# Set correct permissions on environment file (contains credentials!)
sudo chmod 640 /etc/default/minio
sudo chown root:minio-user /etc/default/minio
```

### Step 6: Enable and Start MinIO

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable MinIO to start on boot
sudo systemctl enable minio

# Start MinIO service
sudo systemctl start minio

# Check status
sudo systemctl status minio
```

### Step 7: Verify Installation

```bash
# Check if MinIO is running
sudo systemctl status minio

# Check logs
sudo journalctl -u minio -f

# Check if ports are listening
sudo ss -tuln | grep -E '9000|9001'
```

**Access:**
- API: http://your-server-ip:9000
- Web Console: http://your-server-ip:9001
- Login: Use credentials from `/etc/default/minio`

---

## Systemd Service Management

### Basic Commands

```bash
# Start MinIO
sudo systemctl start minio

# Stop MinIO
sudo systemctl stop minio

# Restart MinIO
sudo systemctl restart minio

# Check status
sudo systemctl status minio

# Enable auto-start on boot
sudo systemctl enable minio

# Disable auto-start
sudo systemctl disable minio
```

---

## [OPTIONAL] Environment Variables Reference

Edit `/etc/default/minio` to configure:

```bash
# === REQUIRED ===

# Data storage location(s)
MINIO_VOLUMES="/mnt/minio/data"

# Root credentials
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=YourStrongPassword123!

# === OPTIONAL ===

# Console address
MINIO_OPTS="--console-address :9001"

# Region name (for AWS compatibility)
MINIO_REGION_NAME=us-east-1

# Site/deployment name
MINIO_SITE_NAME=production-minio

# Enable/disable web browser
MINIO_BROWSER=on

# Server URL (when behind reverse proxy)
MINIO_SERVER_URL=https://minio.example.com
MINIO_BROWSER_REDIRECT_URL=https://console.example.com

# Domain for virtual-host-style requests
MINIO_DOMAIN=minio.example.com

# Prometheus metrics
MINIO_PROMETHEUS_AUTH_TYPE=public
MINIO_PROMETHEUS_URL=http://prometheus:9090

# Performance tuning
MINIO_API_REQUESTS_MAX=10000
MINIO_API_REQUESTS_DEADLINE=10s

# Logging
MINIO_LOG_QUERY_URL=on

# Compression
MINIO_COMPRESS_ENABLE=on
MINIO_COMPRESS_EXTENSIONS=".txt,.csv,.json,.log"
MINIO_COMPRESS_MIME_TYPES="text/*,application/json,application/xml"
```

After changing environment variables:

```bash
# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart minio
```

---


## Python Examples

### Python Setup

```bash
pip install minio --break-system-packages
```

---

## Example 1: Basic Connection

```python
from minio import Minio

# Connect to MinIO
client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="YourStrongPassword123!",
    secure=False
)

# Create a bucket
bucket_name = "my-bucket"
if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' created")
```

---

## Example 2: Upload Text File

```python
from minio import Minio
from io import BytesIO

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Write text to MinIO
text = "Hello MinIO!"
data = BytesIO(text.encode('utf-8'))

client.put_object(
    "my-bucket",
    "hello.txt",
    data,
    length=len(text)
)
print("File uploaded!")
```

---

## Example 3: Read Text File

```python
from minio import Minio

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Read text from MinIO
response = client.get_object("my-bucket", "hello.txt")
content = response.read().decode('utf-8')
response.close()

print(content)  # Output: Hello MinIO!
```

---

## Example 4: Upload Local File

```python
from minio import Minio

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Upload file from disk
client.fput_object(
    "my-bucket",
    "myfile.csv",  # Name in MinIO
    "/path/to/local/file.csv"  # Local file path
)
print("File uploaded!")
```

---

## Example 5: Download to Local File

```python
from minio import Minio

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Download file to disk
client.fget_object(
    "my-bucket",
    "myfile.csv",  # File in MinIO
    "/path/to/save/file.csv"  # Where to save
)
print("File downloaded!")
```

---

## Example 6: List All Files

```python
from minio import Minio

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# List all objects in bucket
objects = client.list_objects("my-bucket", recursive=True)

for obj in objects:
    print(f"{obj.object_name} - {obj.size} bytes")
```

---

## Example 7: Delete a File

```python
from minio import Minio

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Delete object
client.remove_object("my-bucket", "hello.txt")
print("File deleted!")
```

---

## Example 8: Complete Script

```python
from minio import Minio
from io import BytesIO

# Initialize client
client = Minio(
    "localhost:9000",
    access_key="admin",
    secret_key="YourStrongPassword123!",
    secure=False
)

# Create bucket
bucket = "test-bucket"
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

# Upload some text
message = "This is a test file"
client.put_object(
    bucket,
    "test.txt",
    BytesIO(message.encode('utf-8')),
    length=len(message)
)

# Read it back
response = client.get_object(bucket, "test.txt")
print("Content:", response.read().decode('utf-8'))
response.close()

# List files
print("\nFiles in bucket:")
for obj in client.list_objects(bucket):
    print(f"  - {obj.object_name}")

# Clean up
client.remove_object(bucket, "test.txt")
print("\nFile deleted!")
```

---

## Run MinIO as Background Service

Create file: `/etc/systemd/system/minio.service`

```ini
[Unit]
Description=MinIO
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/usr/local/bin/minio server /home/youruser/minio-data --console-address ":9001"
Restart=always

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl start minio
sudo systemctl enable minio
sudo systemctl status minio
```

---

## Common Use Cases

### Store JSON Data

```python
import json
from minio import Minio
from io import BytesIO

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Save JSON
data = {"name": "Ship001", "speed": 18.5}
json_bytes = json.dumps(data).encode('utf-8')

client.put_object(
    "my-bucket",
    "data.json",
    BytesIO(json_bytes),
    length=len(json_bytes)
)

# Read JSON
response = client.get_object("my-bucket", "data.json")
loaded_data = json.loads(response.read().decode('utf-8'))
response.close()
print(loaded_data)
```

### Store CSV with Pandas

```python
import pandas as pd
from minio import Minio
from io import BytesIO

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Create DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'value': [10, 20, 30]
})

# Upload CSV
csv_bytes = df.to_csv(index=False).encode('utf-8')
client.put_object(
    "my-bucket",
    "data.csv",
    BytesIO(csv_bytes),
    length=len(csv_bytes)
)

# Download CSV
response = client.get_object("my-bucket", "data.csv")
df_loaded = pd.read_csv(BytesIO(response.read()))
response.close()
print(df_loaded)
```
