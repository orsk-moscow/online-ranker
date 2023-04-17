# Add the myminio host to the MinIO configuration using the provided details.
# The details include the hostname, port, root user and password for the service.
mc config host add myminio http://s3:$MINIO_PORT $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD

# Create a new bucket in the myminio storage service with the provided name.
mc mb myminio/$MINIO_BUCKET

# Set the policy of the bucket to be public.
mc policy set public myminio/$MINIO_BUCKET

# Copy the sessions csv file to the myminio bucket in the specified folder.
mc cp /opt/$MINIO_SESSIONS_CSV myminio/$MINIO_BUCKET/$MINIO_DATA_FOLDER/$MINIO_SESSIONS_CSV

# Copy the weights file to the myminio bucket in the specified folder.
mc cp /opt/$MINIO_WEIGHTS myminio/$MINIO_BUCKET/$MINIO_FOLDER/$MINIO_WEIGHTS

# Copy the venues csv file to the myminio bucket in the specified folder.
mc cp /opt/$MINIO_VENUES_CSV myminio/$MINIO_BUCKET/$MINIO_DATA_FOLDER/$MINIO_VENUES_CSV
