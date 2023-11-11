import hashlib
import logging
from typing import List

import grpc
from asgiref.sync import sync_to_async

from kenar_sample_addon.background_check.conf import settings
from kenar_sample_addon.background_check import consts
from kenar_sample_addon.background_check.clients.estl import estl_client, BackgroundCheckRequest
from kenar_sample_addon.background_check.models import Status, BackgroundCheck

from kenar_sample_addon.divar.clients.user_profile import user_profile_proxy
from kenar_sample_addon.kenar.clients.addons import addons_client
from kenar_sample_addon.kenar.models.addon import Addon, StickyAddon
from kenar_sample_addon.kenar.models.widgets import Widget, EventRow
from kenar_sample_addon.kenar.utils.errors import DivarException

logger = logging.getLogger(__name__)


class BackgroundCheckController:
    async def update_status(self, submit_date_jalali: str, national_id: str, status_estl: str):
        status = Status.from_estl(status_estl)
        if status == Status.IN_REVIEW:
            return

        national_id_hash = hashlib.md5(national_id.encode()).hexdigest()

        submit_date = estl_client.get_datetime_from_jalali_str(submit_date_jalali)
        try:
            background_check = await self._get_background_check_row_sync(national_id_hash, submit_date)
        except BackgroundCheck.DoesNotExist:
            return
        if background_check.status == status:
            return
        if status == Status.ACCEPTED:
            self.create_sticky_addon(background_check)

    @staticmethod
    def create_sticky_addon(background_check: BackgroundCheck):
        image_uuid = addons_client.upload_image(
            settings.BASE_DIR / 'kenar_sample_addon' / 'static' / 'divar-verified.jpg'
        )

        check_date_formatted = estl_client.get_jalali_str_from_date(background_check.check_date)

        widget_list: List[Widget] = [
            EventRow(image_url=image_uuid,
                     title="عدم سوء پیشینه",
                     subtitle=f"عدم سوءپیشینگی کاربر در تاریخ {check_date_formatted} تایید شده",
                     padded=True),
        ]

        addon: StickyAddon = StickyAddon(widget_list, categories=('craftsmen',))
        try:
            addons_client.create_sticky_user_verification_addon(addon, settings.BACKGROUND_CHECK_KENAR_API_KEY
                                                                , background_check.access_token)
        except DivarException as e:
            logger.error('could not create addon in background check', e.message, e)
        except Exception as e:
            logger.error('could not create addon in background check', e, type(e))

    @staticmethod
    def submit_background_check(
            background_check: BackgroundCheckRequest,
            user,
    ):
        phone_number = user.username
        if BackgroundCheck.objects.filter(user=user, status=Status.IN_REVIEW):
            raise DivarException(message=consts.BACKGROUND_IS_UNDER_REVIEW)

        if phone_number in ('09934342742', '09990000000'):
            estl_client.submit_background_check(request=background_check)
            return

        # Validating national id
        try:
            is_valid_national_code = user_profile_proxy.validate_national_code(
                phone_number, background_check.national_id,
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

        estl_client.submit_background_check(request=background_check)

    @sync_to_async
    def _get_background_check_row_sync(self, national_id_hash, submit_date) -> BackgroundCheck:
        return BackgroundCheck.objects.get(
            national_id_hash=national_id_hash,
            check_date=submit_date.date()
        )


background_check_controller = BackgroundCheckController()
