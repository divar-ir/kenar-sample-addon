import urllib.parse
from typing import Optional, Any

import requests
import scrapy as scrapy
from django.conf import settings
from scrapy.http import Response

from kenar_sample_addon.background_check.background_check import background_check_controller

ESTL_HOST = "co.estl.ir"
ESTL_BASE_URL = "https://" + ESTL_HOST


def login_request(callback=None):
    data = {
        "User": settings.BACKGROUND_CHECK_ESTL_USERNAME,
        "Pass": settings.BACKGROUND_CHECK_ESTL_PASSWORD
    }
    if callback is None:
        return scrapy.FormRequest(ESTL_BASE_URL, formdata=data)
    return scrapy.Request(ESTL_BASE_URL, method='POST', body=urllib.parse.urlencode(data),
                          headers={'Content-Type': 'application/x-www-form-urlencoded'}, callback=callback,
                          meta={'handle_httpstatus_list': [307]})


class ESTLListCrawler(scrapy.Spider):
    name = "estl_list_crawler"

    start_urls = [
        'https://co.estl.ir/kartabl/listestl'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        max_number: Optional[int] = None
        for a_element in response.css('ul.pagination li a'):
            a_text = a_element.xpath('./text()').get()

            if a_text is not None and a_text.strip().isdigit():
                number = int(a_text.strip())
                if max_number is None or max_number < number:
                    max_number = number
        for i in range(1, max_number):
            yield scrapy.Request(f'https://co.estl.ir/kartabl/listestl?page={i}', callback=self.parse_table,
                                 dont_filter=True)

    @staticmethod
    async def parse_table(response: Response, **kwargs: Any) -> Any:
        for row in response.css('#example1 tbody tr'):
            datas = [s for s in row.css("td ::text").extract() if s.strip() != '']
            national_id = datas[1].strip()
            status = datas[6].strip()
            registered_date = datas[5]
            await background_check_controller.update_status(
                registered_date,
                national_id,
                status
            )
