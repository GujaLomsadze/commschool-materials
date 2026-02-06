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
