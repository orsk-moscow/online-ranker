# TODO no more need init for the case daily pipeline. So, remove init when it needed
mc config host add myminio http://s3:$MINIO_PORT $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
mc mb myminio/$MINIO_BUCKET
mc policy set public myminio/$MINIO_BUCKET
mc cp /opt/$MINIO_SESSIONS_CSV myminio/$MINIO_BUCKET/$MINIO_DATA_FOLDER/$MINIO_SESSIONS_CSV
mc cp /opt/$MINIO_WEIGHTS myminio/$MINIO_BUCKET/$MINIO_FOLDER/$MINIO_WEIGHTS
mc cp /opt/$MINIO_VENUES_CSV myminio/$MINIO_BUCKET/$MINIO_DATA_FOLDER/$MINIO_VENUES_CSV