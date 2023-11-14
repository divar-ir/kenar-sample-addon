import hashlib
import logging

from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect

from kenar_sample_addon.background_check import consts
from kenar_sample_addon.background_check.background_check import background_check_controller
from kenar_sample_addon.background_check.clients.estl import BackgroundCheckRequest
from kenar_sample_addon.background_check.models import BackgroundCheck, Status
from kenar_sample_addon.oauth import oauth as oauth_controller
from kenar_sample_addon.kenar.utils.errors import DivarException
from kenar_sample_addon.background_check.forms import BackgroundCheckForm
from kenar_sample_addon.oauth.models import OAuth

logger = logging.getLogger(__name__)


def landing(request):
    if request.user.is_authenticated:
        if BackgroundCheck.objects.filter(user=request.user).exists():
            return render(request,
                          'base-container.html',
                          {
                              'contents': 'background_check/result.html',
                              'status': BackgroundCheck.objects.get(user=request.user)
                          })

    return render(
        request,
        'background_check/landing.html'
    )


def start_verification(request):
    oauth_url = oauth_controller.create_redirect_link(
        app_name="background-check",
        request=request,
        scopes=(oauth_controller.create_phone_scope(), oauth_controller.create_sticky_addon_scope()),
        callback_view="background-check:oauth-callback",
    )

    return redirect(oauth_url)


def oauth_callback(request):
    state = request.GET.get("state")
    if state is None:
        return render(
            request,
            "error.html",
        )
    return redirect('background-check:form')


def form(request):
    if not request.user.is_authenticated:
        return render(
            request,
            'error.html'
        )

    if BackgroundCheck.objects.filter(user=request.user).exists():
        return render(request,
                      'base-container.html',
                      {
                          'contents': 'background_check/result.html',
                          'status': BackgroundCheck.objects.get(user=request.user)
                      })

    return render(request, 'base-container.html', {
        'form': BackgroundCheckForm(),
        'contents': 'background_check/form.html'
    })


def verify(request):
    user: User = request.user

    if not user.is_authenticated:
        return render(
            request,
            'error.html'
        )

    if not OAuth.objects.filter(user=request.user).exists():
        return render(
            request,
            'error.html'
        )

    if request.method == "POST":
        background_check_form = BackgroundCheckForm(request.POST)
        if background_check_form.is_valid():
            try:
                background_request = BackgroundCheckRequest(phone_number=user.username,
                                                            **background_check_form.cleaned_data)
                background_check_controller.submit_background_check(background_request, request.user)
                with transaction.atomic():
                    background_check = BackgroundCheck.objects.create(
                        name=background_request.name,
                        family_name=background_request.family_name,
                        national_id_hash=hashlib.md5(background_request.national_id.encode()).hexdigest(),
                        check_date=background_request.registered_date.date(),
                        status=Status.IN_REVIEW,
                        access_token=user.oauth.access_token,
                        user=request.user,
                    )

            except DivarException as e:
                return render(
                    request,
                    'background_check/form.html',
                    {
                        'form': background_check_form,
                        'error': e.message,
                    }
                )
            except Exception as e:
                logger.error("could not verify", user.username, user.id, e)
                return render(
                    request,
                    'background_check/form.html',
                    {
                        'form': background_check_form,
                        'error': consts.UNKNOWN_ERROR,
                    }
                )
            return render(request,
                          'background_check/result.html',
                          {
                              'status': background_check.status
                          })
        else:
            return render(
                request,
                'background_check/form.html',
                {
                    'form': background_check_form,
                }
            )
