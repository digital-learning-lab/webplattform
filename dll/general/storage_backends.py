# -*- coding: utf-8 -*-
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """This is needed to set the static-location"""
    location = 'static'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    """This is needed to set the media-location"""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    """This is currently not used (30.04.20), but might be used for private
    storage.
    """
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
