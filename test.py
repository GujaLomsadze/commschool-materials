from minio import Minio

client = Minio("172.16.33.36:9000", access_key="croco", secret_key="EVJ[Z@a#P427ZcC=", secure=False)

# Upload file from disk
client.remove_bucket("test")
