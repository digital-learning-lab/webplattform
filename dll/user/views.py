import json

from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, FormView, RedirectView
from django.views.generic.base import View
from rest_framework.generics import ListAPIView

from dll.communication.models import CoAuthorshipInvitation, NewsletterSubscrption
from dll.communication.tasks import send_mail
from .forms import (
    UserProfileForm,
    UserEmailsForm,
    UserPasswordChangeForm,
    UserAccountDeleteForm,
)
from dll.content.models import Content, TeachingModule, Tool, Trend, Review
from dll.content.rules import is_bsb_reviewer, is_tuhh_reviewer
from dll.content.serializers import (
    TeachingModuleSerializer,
    ToolSerializer,
    TrendSerializer,
    ContentListInternalSerializer,
    ContentListInternalReviewSerializer,
    ContentListInvitationSerializer,
)
from dll.content.views import BreadcrumbMixin
from dll.user.models import EmailChangeRequest
from dll.user.tokens import account_activation_token, email_confirmation_token
from .forms import SignUpForm
from ..communication.tokens import newsletter_confirm_token

USER_MODEL = get_user_model()


class TestView(TemplateView):
    template_name = "dll/test.html"

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get("user", None)
        if user_id:
            user = USER_MODEL.objects.get(pk=user_id)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return super(TestView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(TestView, self).get_context_data(**kwargs)
        ctx["users"] = USER_MODEL.objects.all()
        ctx["teaching_modules"] = Content.objects.teaching_modules()
        ctx["tools"] = Content.objects.tools()
        ctx["trends"] = Content.objects.trends()
        return ctx


class MyContentView(LoginRequiredMixin, TemplateView, BreadcrumbMixin):
    template_name = "dll/user/content/overview.html"
    breadcrumb_title = "Meine Inhalte"
    breadcrumb_url = reverse_lazy("user-content-overview")


class MyReviewsView(LoginRequiredMixin, TemplateView, BreadcrumbMixin):
    template_name = "dll/user/content/review_content.html"
    breadcrumb_title = "Review Inhalte"
    breadcrumb_url = reverse_lazy("user-content-overview")

    def get_context_data(self, **kwargs):
        ctx = super(MyReviewsView, self).get_context_data(**kwargs)
        user = self.request.user
        base_qs = Content.objects.drafts().filter(
            Q(reviews__status=Review.NEW) | Q(reviews__status=Review.IN_PROGRESS)
        )
        if is_bsb_reviewer(user):
            ctx["contents"] = base_qs.instance_of(TeachingModule)
        elif is_tuhh_reviewer(user):
            ctx["contents"] = base_qs.not_instance_of(TeachingModule)
        elif user.is_superuser:
            ctx["contents"] = base_qs
        # ctx['contents'] = self.request.user.qs_any_content()
        return ctx


class CreateEditContentView(LoginRequiredMixin, TemplateView, BreadcrumbMixin):
    model = None
    serializer = None

    def get_context_data(self, **kwargs):
        ctx = super(CreateEditContentView, self).get_context_data(**kwargs)
        slug = self.kwargs.get("slug", None)
        if slug:
            obj = self.get_object()
            data = self.serializer(obj).data
            if (
                obj
                and obj.review
                and obj.review.status != Review.DECLINED
                and not self.request.user.is_reviewer
            ):
                data["review"] = None
            ctx["obj"] = json.dumps(data)
            ctx["author"] = obj.author.full_name
            ctx["can_delete"] = (
                "true" if self.request.user.has_perm("can_delete", obj) else "false"
            )
        else:
            ctx["author"] = self.request.user.full_name
            ctx["can_delete"] = "true"
        return ctx

    def get_object(self):
        qs = self.model.objects.drafts()
        user = self.request.user
        if not user.is_superuser:
            qs = qs.filter(Q(author=user) | Q(co_authors__in=[user.pk])).distinct()
        if not getattr(self, "object", None):
            slug = self.kwargs.get("slug", None)
            if slug:
                try:
                    self.object = qs.get(slug=slug)
                except ObjectDoesNotExist:
                    raise Http404
        return getattr(self, "object", None)

    def get_breadcrumbs(self):
        bcs = super(CreateEditContentView, self).get_breadcrumbs()
        temp_bc = bcs[1]
        del bcs[1]
        if self.get_object():
            temp_bc["title"] = temp_bc["title"].format("bearbeiten")
        else:
            temp_bc["title"] = temp_bc["title"].format("erstellen")
        bcs.extend(
            [
                {
                    "title": "Meine Inhalte",
                    "url": reverse_lazy("user-content-overview"),
                },
                temp_bc,
            ]
        )
        return bcs


class CreateEditTeachingModuleView(CreateEditContentView):
    template_name = "dll/user/content/add_teaching_module.html"
    breadcrumb_title = "Digitalen Unterrichtsbaustein {}"
    breadcrumb_url = reverse_lazy("add-teaching-module")
    model = TeachingModule
    serializer = TeachingModuleSerializer


class ReviewTeachingModuleView(CreateEditTeachingModuleView):
    template_name = "dll/user/content/review_teaching_module.html"

    def get_breadcrumbs(self):
        bcs = super(CreateEditTeachingModuleView, self).get_breadcrumbs()
        result = []
        result.append(bcs[0])
        result.extend(
            [
                {"title": "Review Inhalte", "url": reverse_lazy("user-content-review")},
                {
                    "title": "Digitalen Unterrichtbaustein reviewen",
                    "url": reverse_lazy("user-content-review"),
                },
            ]
        )
        return result


class CreateEditToolView(CreateEditContentView):
    template_name = "dll/user/content/add_tool.html"
    breadcrumb_title = "Tool {}"
    breadcrumb_url = reverse_lazy("add-tool")
    model = Tool
    serializer = ToolSerializer


class ReviewToolView(CreateEditToolView):
    template_name = "dll/user/content/review_tool.html"

    def get_breadcrumbs(self):
        bcs = super(CreateEditToolView, self).get_breadcrumbs()
        result = []
        result.append(bcs[0])
        result.extend(
            [
                {"title": "Review Inhalte", "url": reverse_lazy("user-content-review")},
                {"title": "Tool reviewen", "url": reverse_lazy("user-content-review")},
            ]
        )
        return result


class CreateEditTrendView(CreateEditContentView):
    template_name = "dll/user/content/add_trend.html"
    breadcrumb_title = "Trend {}"
    breadcrumb_url = reverse_lazy("add-trend")
    model = Trend
    serializer = TrendSerializer


class ReviewTrendView(CreateEditTrendView):
    template_name = "dll/user/content/review_trend.html"

    def get_breadcrumbs(self):
        bcs = super(CreateEditTrendView, self).get_breadcrumbs()
        result = []
        result.append(bcs[0])
        result.extend(
            [
                {"title": "Review Inhalte", "url": reverse_lazy("user-content-review")},
                {"title": "Trend reviewen", "url": reverse_lazy("user-content-review")},
            ]
        )
        return result


class SignUpView(FormView):
    template_name = "dll/user/signup.html"
    form_class = SignUpForm
    email_template = "dll/user/email/account_activation_email.html"
    success_url = reverse_lazy("user:signup-success")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        confirmation_url = reverse(
            "user:activate",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        confirmation_url = self.request.build_absolute_uri(confirmation_url)

        context = {"username": user.full_name, "confirmation_url": confirmation_url}
        send_mail.delay(event_type_code="USER_SIGNUP", email=user.email, ctx=context)

        if form.cleaned_data["newsletter_registration"]:
            try:
                NewsletterSubscrption.objects.get(email=form.cleaned_data["email"])
            except NewsletterSubscrption.DoesNotExist:
                subscription, created = NewsletterSubscrption.objects.update_or_create(
                    email=form.cleaned_data["email"]
                )
                token = reverse(
                    "communication:newsletter-confirm",
                    kwargs={
                        "nl_id_b64": urlsafe_base64_encode(
                            force_bytes(subscription.pk)
                        ),
                        "token": newsletter_confirm_token.make_token(subscription),
                    },
                )
                token = self.request.build_absolute_uri(token)
                form.send_registration_email(token)

        return HttpResponseRedirect(self.get_success_url())


class SignUpSuccessfulView(TemplateView):
    template_name = "dll/user/signup_success.html"


class UserContentView(ListAPIView):
    serializer_class = ContentListInternalSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Content.objects.filter(Q(author=user) | Q(co_authors__in=[user]))

        qs = qs.drafts()

        type = self.request.GET.get("type", None)
        search_term = self.request.GET.get("q", None)
        status = self.request.GET.get("status", None)

        if type == "trend":
            qs = qs.instance_of(Trend)
        if type == "tool":
            qs = qs.instance_of(Tool)
        if type == "teaching-module":
            qs = qs.instance_of(TeachingModule)

        if status == "draft":
            qs = qs.filter(publisher_linked__isnull=True, reviews__isnull=True)
        if status == "submitted":
            qs = qs.filter(
                Q(reviews__status=Review.NEW) | Q(reviews__status=Review.IN_PROGRESS)
            )
        if status == "approved":
            qs = qs.filter(publisher_linked__isnull=False)
        if status == "declined":
            qs = qs.filter(reviews__status=Review.DECLINED)

        if search_term:
            qs = qs.filter(
                Q(name__icontains=search_term) | Q(teaser__icontains=search_term)
            )

        return qs.distinct()


class UserInvitationView(UserContentView):
    serializer_class = ContentListInvitationSerializer

    def get_queryset(self):
        user = self.request.user

        invitation_contents = CoAuthorshipInvitation.objects.filter(
            to=user, accepted=None
        ).values_list("content__pk", flat=True)

        return Content.objects.filter(pk__in=invitation_contents)


def activate_user(
    request, uidb64, token, backend="django.contrib.auth.backends.ModelBackend"
):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = USER_MODEL.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, USER_MODEL.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.doi_confirmed = True
        user.doi_confirmed_date = timezone.now()
        user.save()
        login(request, user, backend=backend)
        return redirect("user-content-overview")
    else:
        return render(request, "dll/user/account_activation_invalid.html")


class PendingReviewContentView(UserContentView):
    serializer_class = ContentListInternalReviewSerializer

    def get_queryset(self):
        reviews = Review.objects.filter(
            is_active=True, status__in=[Review.NEW, Review.IN_PROGRESS]
        )
        qs = Content.objects.drafts().filter(reviews__in=reviews).order_by("created")

        type = self.request.GET.get("type", None)
        search_term = self.request.GET.get("q", None)

        if type == "trend":
            qs = qs.instance_of(Trend)
        if type == "tool":
            qs = qs.instance_of(Tool)
        if type == "teaching-module":
            qs = qs.instance_of(TeachingModule)

        if search_term:
            qs = qs.filter(
                Q(name__icontains=search_term) | Q(teaser__icontains=search_term)
            )

        user = self.request.user

        if user.is_superuser:
            return qs

        if is_tuhh_reviewer(user):
            return qs.not_instance_of(TeachingModule)
        if is_bsb_reviewer(user):
            return qs.instance_of(TeachingModule)

        return qs.none()


class BaseProfileView(FormView, BreadcrumbMixin):
    breadcrumb_title = _("Mein Profil")
    breadcrumb_url = reverse_lazy("user:profile")

    def get_form_kwargs(self):
        kwargs = super(BaseProfileView, self).get_form_kwargs()
        kwargs["instance"] = getattr(self.request, "user", None)
        return kwargs


class ProfileViewIndex(BaseProfileView):
    template_name = "dll/user/profile.html"
    form_class = UserProfileForm


class ProfileViewChangePassword(BaseProfileView):
    template_name = "dll/user/password_change.html"
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("user:profile")

    def get_breadcrumbs(self):
        bcs = super(ProfileViewChangePassword, self).get_breadcrumbs()
        bcs.append(
            {"title": _("Passwort Ändern"), "url": reverse_lazy("user:password_change")}
        )
        return bcs

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class ProfileViewEmails(BaseProfileView):
    template_name = "dll/user/account_email.html"
    form_class = UserEmailsForm
    success_url = reverse_lazy("user:profile")
    INFO_TEXT = _(
        "Es wurde eine E-Mail zur Bestätigung der neuen Adresse versendet. Bitte prüfen Sie Ihr E-Mail "
        "Postfach um die Aktualisierung abzuschließen."
    )

    def get_breadcrumbs(self):
        bcs = super(ProfileViewEmails, self).get_breadcrumbs()
        bcs.append({"title": _("E-Mails"), "url": reverse_lazy("user:email")})
        return bcs

    def form_valid(self, form):
        from dll.communication.tasks import send_mail

        cr = EmailChangeRequest.objects.create(
            user=self.request.user, email=form.cleaned_data["email"]
        )

        confirmation_url = reverse(
            "user:email_confirm",
            kwargs={
                "cr_idb64": urlsafe_base64_encode(force_bytes(cr.pk)),
                "token": email_confirmation_token.make_token(cr),
            },
        )
        confirmation_url = self.request.build_absolute_uri(confirmation_url)

        context = {
            "full_name": self.request.user.full_name,
            "confirmation_url": confirmation_url,
        }

        send_mail.delay(
            event_type_code="USER_EMAIL_CHANGE",
            ctx=context,
            email=form.cleaned_data["email"],
        )

        messages.info(self.request, self.INFO_TEXT)

        return HttpResponseRedirect(self.get_success_url())


def confirm_email(request, cr_idb64, token):
    try:
        cr_id = force_text(urlsafe_base64_decode(cr_idb64))
        cr = EmailChangeRequest.objects.get(pk=cr_id)
    except (TypeError, ValueError, OverflowError, USER_MODEL.DoesNotExist):
        cr = None

    if cr is not None and email_confirmation_token.check_token(cr, token):
        cr.user.email = cr.email
        cr.user.save()
        cr.delete()
        messages.success(request, _("Ihre E-Mail wurde erfolgreich geändert."))
        return redirect("user:profile")
    else:
        messages.warning(request, _("Ihr E-Mail Aktivierungslink ist ungültig."))
        return HttpResponseRedirect("user:profile")


class ProfileViewDelete(BaseProfileView):
    template_name = "dll/user/account_delete.html"
    form_class = UserAccountDeleteForm
    success_url = reverse_lazy("user:account_delete_success")

    def get_breadcrumbs(self):
        bcs = super(ProfileViewDelete, self).get_breadcrumbs()
        bcs.append(
            {"title": _("Account löschen"), "url": reverse_lazy("user:account_delete")}
        )
        return bcs

    def form_valid(self, form):
        user = self.request.user
        user.retire()
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class ProfileViewDeleteSuccess(TemplateView):
    template_name = "dll/user/account_delete_success.html"


class UserFavoriteView(BreadcrumbMixin, TemplateView):
    template_name = "dll/user/content/favorites.html"
    breadcrumb_title = "Mein Merkzettel"
    breadcrumb_url = reverse_lazy("user-favorites-overview")

    def get_context_data(self, **kwargs):
        ctx = super(UserFavoriteView, self).get_context_data(**kwargs)
        ctx["favorites"] = self.request.user.favorites.all()
        return ctx


class FavoriteLoginRequiredView(RedirectView):
    url = reverse_lazy("user:login")
    query_string = True

    def get(self, *args, **kwargs):
        messages.info(
            self.request,
            "Um die Merkzettel-Funktion nutzen zu können, loggen Sie sich bitte ein!",
        )
        return super(FavoriteLoginRequiredView, self).get(*args, **kwargs)
