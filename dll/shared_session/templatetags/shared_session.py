import copy
import json
from urllib.parse import urljoin

import nacl.secret
import nacl.utils
from django import template
from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode

register = template.Library()


@register.tag
def shared_session_loader(parser, token):
    return LoaderNode()


class LoaderNode(template.Node):
    template = template.Template(
        '{% for path in domains %}<script src="{{ path }}" async></script>{% endfor %}'
    )

    def __init__(self):
        self.encryption_key = settings.SECRET_KEY.encode("ascii")[
            : nacl.secret.SecretBox.KEY_SIZE
        ]
        super(LoaderNode, self).__init__()

    def get_domains(self, request):
        host = request.META.get("HTTP_HOST")
        if not host:
            return []

        # Build domain list, with support for subdomains
        domains = copy.copy(settings.SHARED_SESSION_SITES)
        for domain in settings.SHARED_SESSION_SITES:
            if host.endswith(domain):
                domains.remove(domain)

        return domains

    def ensure_session_key(self, request):
        if not request.session.session_key:
            request.session.save()

    def encrypt_payload(self, data):
        box = nacl.secret.SecretBox(self.encryption_key)
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

        message = json.dumps(data).encode("ascii")
        return box.encrypt(message, nonce)

    def get_message(self, request, domain):
        host = request.META.get("HTTP_HOST", None)
        if not host:
            return {}
        enc_payload = self.encrypt_payload(
            {
                "key": request.session.session_key,
                "src": host,
                "dst": domain,
                "ts": timezone.now().isoformat(),
            }
        )
        data = urlsafe_base64_encode(enc_payload)
        try:
            return data.decode("ascii")
        except AttributeError:
            return data

    def build_url(self, domain, message):
        return urljoin(
            domain, reverse("shared_session:share", kwargs={"message": message})
        )

    def render(self, context):
        request = context.get("request", None)

        if not request or request.session.is_empty():
            return ""

        try:
            self.ensure_session_key(request)

            return self.template.render(
                template.Context(
                    {
                        "domains": [
                            self.build_url(
                                domain="{}://{}".format(request.scheme, domain),
                                message=self.get_message(request, domain),
                            )
                            for domain in self.get_domains(request)
                        ]
                    }
                )
            )
        except UpdateError:
            return ""
