import requests
import lxml.html
import pprint

html = requests.get("http://www.daytonlocal.com/listings/gounaris-denslow-abboud.asp").content
dom = lxml.html.fromstring(html)

pp = pprint.PrettyPrinter(indent=4)

entry = dom.cssselect('div.vcard')[0]
post = {
        'name': entry.cssselect('.fn')[0].text_content(),
        'website': entry.cssselect('.fn a')[0].get('href'),
        'logo': 'http://www.daytonlocal.com'+dom.cssselect('#MainContentArea img')[0].get('src'),
        'address1': entry.cssselect('.street-address')[0].text_content(),
        'address2': entry.cssselect('.adr')[0],
        'city': entry.cssselect('.locality')[0].text_content(),
        'state': entry.cssselect('.region')[0].text_content(),
        'zip': entry.cssselect('.postal-code')[0].text_content(),
        'phone': entry.cssselect('.clearl')[0].text_content(),
        'description': entry.cssselect('.clearl')[2].text_content(),
        'facebook': entry.cssselect('.clearl')[1],
        'twitter': entry.cssselect('.clearl')[1]
}

pp.pprint(post)
