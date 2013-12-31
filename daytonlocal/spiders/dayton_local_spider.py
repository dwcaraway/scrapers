__author__ = 'dwcaraway'

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
import urlparse
import re
import lxml
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
        return [Request(url=link, callback=self.paginate) for link in links if not link.startswith('#')]

    def paginate(self, response):
        sel = Selector(response)
        links = sel.xpath("//div[contains(@class,'dright')]/a/ @href").extract()
        link_req_objs = [Request(url=link, callback=self.extract) for link in links]
        next_url = sel.xpath("//a[text()='Next']/@href").extract()
        if next_url:
            link_req_objs.append(Request(url=urlparse.urljoin(response.url, next_url[0]), callback=self.paginate))

        return link_req_objs


    def extract(self, response):

        sel = Selector(response)

        dom = lxml.html.fromstring(response.body)

        logo = sel.xpath('//*[@id="MainContentArea"]//div[contains(@class, "dright")]/a/img/ @src').extract()


        entry = dom.cssselect('div.vcard')[0]

        item = DaytonlocalItem()

        items = []

        for card in sel.xpath('//div[contains(@class, "vcard")]'):

            name = card.xpath('//*[contains(@class, "fn")]//strong/text()').extract()
            item['name'] = name[0] if name else None

            website = card.xpath('//*[contains(@class, "fn")]//a/ @href').extract()
            item['website'] = website[0].get('href') if website else None

            item['logo'] = urlparse.urljoin('http://www.daytonlocal.com', logo[0]) if logo else None

            address1 = card.xpath('//span[contains(@class, "street-address")]/text()').extract()
            item['address1'] = address1[0] if address1 else None

            address2 = entry.cssselect('.adr br')
            item['address2'] = address2[0].tail if address2 else None

            city = card.xpath('//span[contains(@class, "locality")]/text()').extract()
            item['city'] = city[0] if city else None

            state = card.xpath('//span[contains(@class, "region")]/text()').extract()
            item['state'] = state[0] if state else None

            zipcode = card.xpath('//span[contains(@class, "postal-code")]/text()').extract()
            item['zip'] = zipcode[0] if zipcode else None

            phone =entry.cssselect('.clearl')
            item['phone'] = phone[0].text_content() if phone else None

            descr = entry.cssselect('.clearl')
            item['description'] = descr[2].text_content() if descr else None

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

            items.append(item)

        return items
