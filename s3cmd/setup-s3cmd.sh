#!/bin/sh

#
# Check for required parameters
#
if [ -z "${BUCKET_NAME_FROM}" ]; then
    echo "ERROR: The environment variable BUCKET_NAME is not set."
    exit 1
fi

if [ -z "${HOST_BUCKET_FROM}" ]; then
    echo "ERROR: The environment variable HOST_BUCKET is not set."
    exit 1
fi

if [ -z "${BUCKET_NAME_TO}" ]; then
    echo "ERROR: The environment variable BUCKET_NAME is not set."
    exit 1
fi

if [ -z "${HOST_BUCKET_TO}" ]; then
    echo "ERROR: The environment variable HOST_BUCKET is not set."
    exit 1
fi

if [ -z "${ACCESS_KEY}" ]; then
    echo "ERROR: The environment variable ACCESS_KEY is not set."
    exit 1
fi

if [ -z "${SECRET_KEY}" ]; then
    echo "ERROR: The environment variable SECRET_KEY is not set."
    exit 1
fi

#
# create the s3cfg-files
# add bucket, key and secret
#
cp /opt/.s3cfg /.s3cfg-from
echo "" >> /.s3cfg-from
echo "host_bucket = ${HOST_BUCKET_FROM}" >> /.s3cfg-from
echo "access_key = ${ACCESS_KEY}" >> /.s3cfg-from
echo "secret_key = ${SECRET_KEY}" >> /.s3cfg-from

cp /opt/.s3cfg /.s3cfg-to
echo "" >> /.s3cfg-to
echo "host_bucket = ${HOST_BUCKET_TO}" >> /.s3cfg-to
echo "access_key = ${ACCESS_KEY}" >> /.s3cfg-to
echo "secret_key = ${SECRET_KEY}" >> /.s3cfg-to

#
# Finished setup
#
echo "Finished s3cmd setup"