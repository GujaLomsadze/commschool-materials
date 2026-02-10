from minio import Minio

client = Minio("localhost:9000", access_key="admin", secret_key="YourStrongPassword123!", secure=False)

# Upload file from disk
client.fput_object(
    "my-bucket",
    "/data/2026/misc/minio_guide.md",  # Name in MinIO
    "minio_guide.md"  # Local file path
)
print("File uploaded!")


"/data/2026/misc/minio_guide.md"