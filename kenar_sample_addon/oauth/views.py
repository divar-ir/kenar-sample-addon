import logging
import re

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

import kenar_sample_addon.oauth.oauth as oauth_controller
from kenar_sample_addon.oauth.models import Scope, OAuth

logger = logging.getLogger(__name__)

scope_regex = re.compile(r"^(?P<permission_type>([A-Z]+_)*([A-Z]+))(__(?P<resource_id>.+))?$")


@transaction.atomic
def oauth_callback(request):
    oauth_session = request.session.get(settings.OAUTH_INFO_SESSION_KEY, None)
    if oauth_session is None:
        return render(
            request,
            "error.html"
        )

    del (request.session[settings.OAUTH_INFO_SESSION_KEY])

    app_name, state_in_session, scopes, callback_view, oauth_url = oauth_session["app_name"], oauth_session["state"], \
        oauth_session["scopes"], oauth_session["callback_view"], oauth_session["oauth_url"]

    code = request.GET.get("code")
    state = request.GET.get("state")
    if code is None or state is None:
        return render(
            request,
            "oauth-canceled.html",
            context={"oauth_url": oauth_url}
        )

    if state != state_in_session:
        return render(
            request,
            'error.html'
        )

    oauth_data = oauth_controller.get_oauth(code=code, app_name=app_name)
    try:
        phones = oauth_controller.get_phone_numbers(app_name, oauth_data.access_token)
    except Exception as e:
        logger.error("got exception while getting phone number", e)
        return JsonResponse({"status": "something bad happened"})
    phone = phones[0]

    user, created = User.objects.get_or_create(username=phone)
    login(request, user)

    if not created:
        OAuth.objects.filter(user=user).delete()

    oauth_data.user = user
    oauth_data.save()

    scopes_permissions = []
    for s in scopes:
        scope_match_groups = scope_regex.search(s).groupdict()
        scopes_permissions.append(scope_match_groups['permission_type'])

        Scope.objects.create(
            permission_type=scope_match_groups['permission_type'],
            resource_id=scope_match_groups.setdefault('resource_id', None),
            oauth=oauth_data
        )

    return redirect(reverse(callback_view) + f'?state={state}')
