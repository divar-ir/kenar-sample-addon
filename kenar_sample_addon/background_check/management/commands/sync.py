from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from kenar_sample_addon.background_check.estl_crawler import settings as estl_crawler_settings
from kenar_sample_addon.background_check.estl_crawler.spiders.estl import ESTLListCrawler


class Command(BaseCommand):
    help = "syncs background checks with ESTL"

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(estl_crawler_settings)

        process = CrawlerProcess(settings=crawler_settings)

        process.crawl(ESTLListCrawler)
        process.start()

