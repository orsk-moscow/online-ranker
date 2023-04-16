mc config host add myminio http://s3:$MINIO_PORT $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
mc mb myminio/$MINIO_BUCKET
mc policy set public myminio/$MINIO_BUCKET
mc cp /opt/sessions.csv myminio/$MINIO_BUCKET
mc cp /opt/model.cbm myminio/$MINIO_BUCKET/$MINIO_FOLDER/$MINIO_WEIGHTS