# -*- coding: utf-8 -*-
import scrapy


class RosaSpider(scrapy.Spider):
    name = 'rosa'
    allowed_domains = ['inter03.tse.jus.br']
    start_urls = ['http://inter03.tse.jus.br/']

    def parse(self, response):
        pass
