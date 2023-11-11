import logging

from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect

from kenar_sample_addon.oauth import oauth as oauth_controller
from kenar_sample_addon.real_estate_verification import verification, consts
from kenar_sample_addon.real_estate_verification.forms import VerificationForm
from kenar_sample_addon.real_estate_verification.models import VerifiedPost
from kenar_sample_addon.kenar.utils.errors import DivarException

logger = logging.getLogger(__name__)


def landing(request):
    token = request.GET.get("post_token")
    if token is None:
        return render(
            request,
            "error.html"
        )

    if request.user.is_authenticated:
        if VerifiedPost.objects.filter(user=request.user, post_token=token).exists():
            return render(request,
                          'base-container.html',
                          {
                              'token': token,
                              'contents': 'real_estate/result.html'
                          })

    return render(
        request,
        'real_estate/landing.html',
        {
            "token": token,
        }
    )


def start_verification(request):
    token = request.GET.get("token")
    if token is None:
        return render(
            request,
            "error.html"
        )

    oauth_url = oauth_controller.create_redirect_link(
        app_name='real-estate-verification',
        request=request,
        scopes=(oauth_controller.create_phone_scope(), oauth_controller.create_approved_addon_scope(token)),
        callback_view="real-estate:oauth-callback",
        state_data=token
    )

    return redirect(oauth_url)


def oauth_callback(request):
    state = request.GET.get("state")
    if state is None:
        return render(
            request,
            "error.html",
        )

    token = oauth_controller.extract_state_data(state)
    return redirect('real-estate:form', token=token)


def form(request, token):
    if not request.user.is_authenticated:
        return render(
            request,
            'error.html'
        )

    return render(request, 'base-container.html', {
        'form': VerificationForm(),
        'token': token,
        'contents': 'real_estate/form.html'
    })


def verify(request, token):
    user: User = request.user

    if not user.is_authenticated:
        return render(
            request,
            'error.html'
        )

    if request.method == "POST":
        verification_form = VerificationForm(request.POST)
        if verification_form.is_valid():
            postal_code = verification_form.cleaned_data['postal_code']
            national_id = verification_form.cleaned_data['national_id']
            try:
                with transaction.atomic():
                    verification.verify_by_postal_code(token, user, national_id, postal_code)
                    verification.create_verified_addon(token, user.oauth)
            except DivarException as e:
                return render(
                    request,
                    'real_estate/form.html',
                    {
                        'form': verification_form,
                        'error': e.message,
                        'token': token,
                    }
                )
            except Exception as e:
                logger.error("could not verify", token, postal_code, user.id, e)
                return render(
                    request,
                    'real_estate/form.html',
                    {
                        'form': verification_form,
                        'error': consts.UNKNOWN_ERROR,
                        'token': token,
                    }
                )
            return render(request,
                          'real_estate/verified.html',
                          {
                              'token': token
                          })
        else:
            return render(
                request,
                'real_estate/form.html',
                {
                    'form': verification_form,
                    'token': token,
                }
            )
