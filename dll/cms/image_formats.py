from wagtail.images.formats import Format, register_image_format

register_image_format(
    Format("thumbnail", "Thumbnail", "richtext-image thumbnail", "max-120x120")
)
