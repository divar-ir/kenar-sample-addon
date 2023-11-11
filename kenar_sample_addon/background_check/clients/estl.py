import datetime
import logging
from typing import Dict, Union

import xmltodict
from jinja2 import Template

from django.conf import settings
from persiantools.jdatetime import JalaliDateTime
from persian_tools import phone_number as phone_number_utils
from kenar_sample_addon.background_check import consts
from kenar_sample_addon.kenar.utils.errors import DivarException
from kenar_sample_addon.kenar.utils.proxy import DivarHTTPProxy

logger = logging.getLogger(__name__)


class ESTLClient(DivarHTTPProxy):
    _datetime_time_format = "%Y/%m/%d %H:%M:%S"
    _date_time_format = "%Y/%m/%d"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(settings.BASE_DIR / "kenar_sample_addon" / "background_check" / "clients" /
                  "background_check_request_template.xml", "r") as template_file:
            self._xml_template = Template(template_file.read())

    @classmethod
    def get_datetime_from_jalali_str(cls, jalali_date: str):
        return JalaliDateTime.strptime(data_string=jalali_date, fmt=cls._datetime_time_format)

    @classmethod
    def get_jalali_str_from_datetime(cls, date: datetime.datetime):
        return JalaliDateTime(date).strftime(fmt=cls._datetime_time_format, locale="en")

    @classmethod
    def get_jalali_str_from_date(cls, date: datetime.date):
        return JalaliDateTime(datetime.datetime.combine(date, datetime.datetime.min.time())). \
            strftime(fmt=cls._date_time_format, locale="en")

    @classmethod
    def get_datetime_from_jalali_str(cls, jalali_date: str):
        return JalaliDateTime.strptime(data_string=jalali_date, fmt=cls._datetime_time_format)

    @classmethod
    def get_jalali_str_from_datetime(cls, date: datetime.datetime):
        return JalaliDateTime(date).strftime(fmt=cls._datetime_time_format, locale="en")

    def submit_background_check(self, request: "BackgroundCheckRequest"):
        req_data = request.get_request()
        req_data['terminal_id'] = settings.BACKGROUND_CHECK_ESTL_WSDL_TERMINAL_ID
        req_data['password'] = settings.BACKGROUND_CHECK_ESTL_WSDL_PASSWORD
        req_data['estl_wsdl_url'] = settings.BACKGROUND_CHECK_ESTL_WSDL_URL

        xml_req = self._xml_template.render(req_data).encode('utf-8')
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://WebService.tsinco.com/ESTL/SendInquiryRequestPersonRequest"
        }

        resp = self._post(settings.BACKGROUND_CHECK_ESTL_WSDL_URL, data=xml_req, headers=headers)
        resp_xml = xmltodict.parse(resp.content)
        code = int(resp_xml['S:Envelope']['S:Body']['ns2:SendInquiryRequestPersonResponse']['return'])
        self.raise_error(code)

    @classmethod
    def raise_error(cls, code):
        match code:
            case 1:
                return
            case 0, 3, 4, 17, 19, 300:
                raise DivarException(message=consts.UNKNOWN_ERROR)
            case 2:
                raise DivarException(message=consts.DUPLICATE_REQUEST)
            case 6:
                raise DivarException(message=consts.EMPTY_REQUEST_FIELD)
            case 7:
                raise ValueError("invalid date format in estl client")
            case 8:
                raise ValueError("invalid date format in estl client")
            case 18:
                raise ValueError("invalid phone format in estl client")
            case 100:
                raise ValueError("invalid national id")
            case _:
                logger.error("invalid response code in estl client", code)
                raise Exception("invalid response code", code)


class BackgroundCheckRequest:
    def __init__(self,
                 name,
                 family_name,
                 father_name,
                 national_id,
                 identity_id,
                 birth_date: Union[JalaliDateTime, datetime.date, datetime.datetime, str],
                 phone_number):
        self.name = name
        self.family_name = family_name
        self.father_name = father_name
        self.national_id = national_id
        self.identity_id = identity_id
        if isinstance(birth_date, (datetime.datetime, JalaliDateTime)):
            self.birth_date = estl_client.get_jalali_str_from_date(birth_date.date())
        elif isinstance(birth_date, datetime.date):
            self.birth_date = estl_client.get_jalali_str_from_date(birth_date)
        else:
            self.birth_date = birth_date

        # TODO: remove this after everything worked fine
        if phone_number == "09990000000":
            phone_number = "+989990000000"
        else:
            phone_number = phone_number_utils.normalize(phone_number, "+98")
        self.phone_number = phone_number
        self.registered_date = datetime.datetime.now()
        self.registered_date_persian_str = estl_client.get_jalali_str_from_date(self.registered_date.date())

    def get_request(self) -> Dict[str, str]:
        return {
            'national_id': self.national_id,
            'first_name': self.name,
            'last_name': self.family_name,
            'father_name': self.father_name,
            'birth_date': self.birth_date,
            'identity_id': self.identity_id,
            'registered_date': self.registered_date_persian_str,
            'mobile': self.phone_number,
        }


estl_client = ESTLClient.get_instance(max_retry=3)
