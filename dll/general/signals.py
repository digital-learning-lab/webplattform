from django.dispatch import Signal


post_publish = Signal(providing_args=['instance'])
post_unpublish = Signal(providing_args=['instance'])
