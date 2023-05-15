from django.conf import settings
from django.template.loader import get_template
from wagtail.embeds.finders.oembed import OEmbedFinder


class LazyOEmbedFinder(OEmbedFinder):
    def lazify_embed_html(self, html, url):
        # transform youtube url to youtube embed url
        if "watch" in url:
            url = url.replace("watch?v=", "embed/")
        if "youtub.be/" in url:
            url = url.replace(".be/", ".com/embed/")

        t = get_template("dll/content/video_lazy_loader.html")
        ctx = {"url": url}
        if settings.SITE_ID == 1:
            ctx.update(
                {
                    "logo_mobile_1x": "img/logo/dll_logo_rgb_ohne_claim.png",
                }
            )
        elif settings.SITE_ID == 2:
            ctx.update(
                {
                    "logo_mobile_1x": "img/logo/logo_dlt_mobile.svg",
                }
            )
        content = t.render(ctx)
        content = content.replace('"', "'")
        srcdoc = f'srcdoc="{content}"'

        html = html.replace("<iframe ", f"<iframe {srcdoc} data-embed")
        return html

    def find_embed(self, url, max_width=None, max_height=None):
        result = super(LazyOEmbedFinder, self).find_embed(
            url, max_width=max_width, max_height=max_height
        )
        if "html" in result:
            result["html"] = self.lazify_embed_html(result["html"], url)
        return result


embed_finder_class = LazyOEmbedFinder
