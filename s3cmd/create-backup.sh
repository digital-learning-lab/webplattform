#!/bin/sh

TIMESTAMP=$(date +%y%m%d-%H%M%S)
echo "sync s3 into /data/"
s3cmd --config=/.s3cfg-from sync s3://$BUCKET_NAME_FROM /data/;
echo "compress synced data"
tar cvfz $TIMESTAMP.tar.gz /data/;
echo "upload .tar.gz with synced data to backup bucket"
s3cmd --config=/.s3cfg-to put $TIMESTAMP.tar.gz s3://$BUCKET_NAME_TO;
echo "remove local .tar.gz"
rm $TIMESTAMP.tar.gz

echo "finished backup creation"