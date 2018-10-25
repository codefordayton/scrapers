__author__ = 'dwcaraway'

from scrapy.spider import Spider
from scrapy.selector import Selector
import urlparse
import urllib2
import lxml
import datetime
from dayton.items import DaytonOhioPDFItem
from scrapy.http import Request


class DaytonOhioPDFSpider(Spider):
    """Crawls daytonohio.gov looking for PDF documents"""
    name = "daytonohio_rss_pdf"
    template_url = 'http://daytonohio.gov/Search/_layouts/srchrss.aspx?k=pdf&start=%d'  # noqa
    allowed_domains = ["daytonohio.gov"]
    start_urls = [
        template_url % 1
    ]

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//item')

        results = []

        for item in items:
            result_item = DaytonOhioPDFItem()
            title = item.xpath('title/text()').extract()
            url = item.xpath('link/text()').extract()
            author = item.xpath('author/text()').extract()
            pubDate = item.xpath('pubDate/text()').extract()

            result_item['title'] = title[0] if title else None
            result_item['url'] = url[0] if url else None
            result_item['author'] = author[0] if author else None
            result_item['pubDate'] = pubDate[0] if pubDate else None

            results.append(result_item)

        if items:
            query_args = urlparse.parse_qs(
                urlparse.urlparse(response.url).query)
            current = int(query_args['start'][0])
            new_url = self.template_url % (current + len(items))
            results.append(Request(url=new_url, callback=self.parse))

        return results


if __name__ == '__main__':
    # Run data extraction test on individual page
    urls = ["http://daytonohio.gov/Search/_layouts/srchrss.aspx?k=pdf&start=1"]
    import requests
    from scrapy.http import Request
    from scrapy.http.response.xml import XmlResponse

    for url in urls:
        request = Request(url=url)
        response = XmlResponse(url=url, request=request,
                               body=requests.get(url).text, encoding='utf-8')

        print(DaytonOhioPDFSpider.parse(DaytonOhioPDFSpider(),
                                        response=response))
