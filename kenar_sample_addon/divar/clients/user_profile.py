
from kenar_sample_addon.kenar.utils.proxy import DivarGRPCProxy
from divar_rpc import DivarServices

from divar_interface.user_profile.user_profile_pb2 import *


class UserProfileProxy(DivarGRPCProxy):
    """ get proxy by calling UserProfileProxy.get_instance() """

    service_name = DivarServices.USER_PROFILE

    def validate_national_code(self, phone_number, national_code):
        request = VerifyUserRequest(
            no_cache=False,
            phone=phone_number,
            no_retry=True,
            verification_source=VERIFICATION_SOURCE_SUBMIT,
        )
        request.iranian_identity_info.national_id = national_code
        response:  VerifyUserResponse = self.VerifyUser(request)
        return response.verification_state == VERIFICATION_STATE_VERIFIED


user_profile_proxy = UserProfileProxy.get_instance()
