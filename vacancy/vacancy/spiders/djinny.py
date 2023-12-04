from typing import Iterable

import scrapy
from scrapy.http import Response
from .config import PYTHON_TECHNOLOGIES


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    all_techs = dict()

    def start_requests(self) -> Iterable[scrapy.Request]:
        url = "https://djinni.co/jobs/?primary_keyword=Python"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response):
        for vacancy in response.css(".job-list__item"):
            yield scrapy.Request(
                response.urljoin(
                    vacancy.css(".job-list-item__link::attr(href)").get()
                ),
                callback=self.parse_single,
            )

        if last_page_url := response.css(
            ".pagination li:last-child a::attr(href)"
        ).get():
            yield response.follow(last_page_url, callback=self.parse)

    @staticmethod
    def parse_single(response):
        technologies = VacanciesSpider.parse_technologies(response)
        return {
            "company": response.css(".job-details--title::text").get().strip(),
            "title": response.css("h1::text").get().strip(),
            "technologies": technologies,
            "url": response.url,
        }

    @staticmethod
    def parse_technologies(response):
        cleaned_technologies = []

        description = "".join(
            response.css(
                "div.mb-4::text"
            ).getall()
        ).lower()
        technologies = "".join(
            response.css(
                'div.job-additional-info--item-text > span[class=""]::text'
            ).getall()
        ).lower()

        for tech in PYTHON_TECHNOLOGIES:
            if (
                tech.lower() in technologies
                or tech.lower() in description
                and tech not in cleaned_technologies
            ):
                cleaned_technologies.append(tech)
        return cleaned_technologies
