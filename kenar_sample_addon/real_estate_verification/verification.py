import logging
from typing import List

import grpc
from kenar_sample_addon.real_estate_verification.conf import settings
from django.contrib.auth.models import User

from kenar_sample_addon.kenar.clients.addons import addons_client
from kenar_sample_addon.kenar.clients.finder import finder_client, FinderException
from kenar_sample_addon.kenar.models.addon import Addon
from kenar_sample_addon.kenar.models.widgets import *
from kenar_sample_addon.oauth.models import OAuth
from kenar_sample_addon.real_estate_verification import postal_code_range, consts
from kenar_sample_addon.real_estate_verification.clients.eskan_client import eskan_proxy, \
    EskanProxyException
from kenar_sample_addon.divar.clients import user_profile_proxy
from kenar_sample_addon.real_estate_verification.models import VerifiedPost
from kenar_sample_addon.kenar.utils.errors import DivarException

logger = logging.getLogger(__name__)


def verify_by_postal_code(token: str, user: User, national_id: str, postal_code: str):
    phone_number = user.username

    if VerifiedPost.objects.filter(postal_code=postal_code).exists():
        try:
            if finder_client.does_post_exist(token, api_key=settings.REAL_ESTATE_VERIFICATION_KENAR_API_KEY):
                logger.warning('Exising PostalCode verification tried', extra={'postal_code': postal_code})
                raise DivarException(message=consts.OWNERSHIP_ALREADY_TAKEN)
            else:
                VerifiedPost.objects.get(postal_code=postal_code).delete()
        except FinderException as e:
            logger.error("post exists check failed", token, e)
            raise DivarException(message=consts.UNKNOWN_ERROR)

    try:
        post = finder_client.get_post(token=token, api_key=settings.REAL_ESTATE_VERIFICATION_KENAR_API_KEY)
    except FinderException as e:
        logger.error("could not get post", *e.args)
        raise DivarException(message=consts.UNKNOWN_ERROR)

    if post.category not in ('apartment-sell', 'apartment-rent'):
        logger.warning('invalid category for post', extra={
            'token': post.token,
            'phone': phone_number,
            'category': post.category,
        })
        raise DivarException(message=consts.INVALID_CATEGORY)

    if not postal_code_range.is_valid_postal_code_for_city(post.city, postal_code):
        logger.warning('Invalid PostalCode for region tried', extra={
            'postal_code': postal_code, 'city': post.city,
        })
        raise DivarException(message=consts.POSTAL_CODE_NOT_VALID_FOR_LOCATION)

    # Todo remove this code used for testing
    if phone_number == '09990000000' and national_id == "1234567890":
        v = VerifiedPost(
            post_token=token,
            postal_code=postal_code,
            user=user,
        )
        v.save()
        return

    try:
        is_valid_national_code = user_profile_proxy.validate_national_code(
            phone_number, national_id,
        )
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.PERMISSION_DENIED:
            logger.warning('Too many national_id validation tries', extra={'phone': phone_number})
            raise DivarException(message=consts.NATIONAL_ID_TRIED_TOO_MUCH)
        else:
            logger.exception('failed calling user_profile.validate_national_code')
            raise DivarException(message=consts.UNKNOWN_ERROR)

    if not is_valid_national_code:
        raise DivarException(message=consts.NATIONAL_ID_IS_NOT_YOURS)

    try:
        is_verified = eskan_proxy.verify_ownership(national_id, postal_code)
    except EskanProxyException:
        raise DivarException(message=consts.ESKAN_PROXY_IS_DOWN)

    if is_verified:
        VerifiedPost(
            post_token=token,
            postal_code=postal_code,
            user=user,
        ).save()
    else:
        raise DivarException(message=consts.OWNERSHIP_NOT_VERIFIED)


def create_verified_addon(token: str, oauth: OAuth):
    if oauth.approved_addon_token() != token:
        raise DivarException(message=consts.UNKNOWN_ERROR)

    image_uuid = addons_client.upload_image(
        settings.BASE_DIR / 'kenar_sample_addon' / 'static' / 'divar-verified.jpg'
    )

    widget_list: List[Widget] = [
        EventRow(image_url=image_uuid,
                 title="کد‌پستی",
                 subtitle="کد‌پستی با کد‌ملی تطبیق داده‌شده",
                 padded=True)
    ]

    addon: Addon = Addon(widget_list)

    addons_client.create_post_addon(token, addon, settings.REAL_ESTATE_VERIFICATION_KENAR_API_KEY, oauth.access_token)
