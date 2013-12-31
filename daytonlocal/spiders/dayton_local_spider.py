__author__ = 'dwcaraway'

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
import urlparse
import re
import lxml
import requests
from daytonlocal.items import DaytonlocalItem

facebook_matcher = re.compile('.*GoHere=(.*facebook.*)')
twitter_matcher = re.compile('.*GoHere=(.*twitter.*)')
category_matcher = re.compile('.*[.]com/(.*)[.]asp')

class DaytonLocalSpider(BaseSpider):
    name = "dayton_local"
    allowed_domains = ["daytonlocal.com"]
    start_urls = [
        "http://www.daytonlocal.com/directory.asp"
    ]

    def parse(self, response):
        sel = Selector(response)
        links = sel.css('#MainContentArea div.clearc a').xpath('@href').extract()
        return [Request(url=link, callback='paginate') for link in links if not link.startswith('#')]


    def paginate(self, response):
        sel = Selector(response)
        links = sel.xpath("//div[contains(@class,'dright')]/a/ @href").extract()
        link_req_objs = [Request(url=link, callback='extract') for link in links]
        next_url = sel.xpath("//a[text()='Next']/@href").extract()
        if next_url:
            link_req_objs.append(Request(url=urlparse.urljoin(response.url, next_url[0]), callback='paginate'))

        return link_req_objs


    def extract(self, response):

        dom = lxml.html.fromstring(response.text)

        entry = dom.cssselect('div.vcard')[0]
        data = {
                'name': entry.cssselect('.fn')[0].text_content(),
                'website': entry.cssselect('.fn a')[0].get('href'),
                'logo': 'http://www.daytonlocal.com'+dom.cssselect('#MainContentArea img')[0].get('src'),
                'address1': entry.cssselect('.street-address')[0].text_content(),
                'address2': entry.cssselect('.adr br')[0].tail,
                'city': entry.cssselect('.locality')[0].text_content(),
                'state': entry.cssselect('.region')[0].text_content(),
                'zip': entry.cssselect('.postal-code')[0].text_content(),
                'phone': entry.cssselect('.clearl')[0].text_content(),
                'description': entry.cssselect('.clearl')[2].text_content(),
        }

        item = DaytonlocalItem(**data)

        #social media links
        links = entry.cssselect('.clearl')[1].cssselect('a')
        for link in links:
            href = link.get('href')
            if 'facebook' in href:
                item['facebook'] = facebook_matcher.match(href).group(1)
            elif 'twitter' in href:
                item['twitter'] = twitter_matcher.match(href).group(1)
            else:
                match = category_matcher.match(href)
                if match:
                    item['category'] = match.group(1).split('/')

        #Strip all strings
        for k, v in item.iteritems():
            if isinstance(v, basestring):
                item[k] = v.strip()

        return item

DaytonLocalSpider().extract(requests.get('http://www.daytonlocal.com/listings/tint-masters.asp'))

    # def extract(self, response):
    #
    #
    #
    #     sel = Selector(response)
    #     entry = sel.css('div.vcard')[0]
    #     item = DaytonlocalItem(
    #             name=sel.xpath("//*[contains(@class, 'fn')]/a/ @href").extract()[0],
    #             website=sel.xpath("//*[contains(@class, 'fn')]/a/ @href").extract()[0],
    #             logo=urlparse.urljoin('http://www.daytonlocal.com', sel.xpath('//*[@id="MainContentArea"]/div[1]/div[1]/a/img/ @src').extract()[0]),
    #             address1=sel.xpath("//*[contains(@class, 'street-address')]/text()").extract()[0],
    #
    #             address2=entry.css('.adr br')[0].tail,
    #             city=entry.css('.locality')[0].text_content(),
    #             state=entry.css('.region')[0].text_content(),
    #             zip=entry.css('.postal-code')[0].text_content(),
    #             phone=entry.css('.clearl')[0].text_content(),
    #             description=entry.css('.clearl')[2].text_content()
    #     )
    #
    #     #social media links
    #     links = entry.css('.clearl')[1].css('a')
    #     for link in links:
    #         href = link.get('href')
    #         if 'facebook' in href:
    #             item.facebook = facebook_matcher.match(href).group(1)
    #         elif 'twitter' in href:
    #             item.twitter = twitter_matcher.match(href).group(1)
    #         else:
    #             match = category_matcher.match(href)
    #             if match:
    #                 item.category = match.group(1).split('/')
    #
    #     #Strip all strings
    #     for k, v in item.iteritems():
    #         if isinstance(v, basestring):
    #             item[k] = v.strip()
    #
    #     return item


