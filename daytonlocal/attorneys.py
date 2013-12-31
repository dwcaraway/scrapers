import requests
import lxml.html
import pprint
import re
import string

html = requests.get("http://www.daytonlocal.com/directory.asp").content
dom = lxml.html.fromstring(html)

pp = pprint.PrettyPrinter(indent=4)

facebook_matcher = re.compile('.*GoHere=(.*facebook.*)')
twitter_matcher = re.compile('.*GoHere=(.*twitter.*)')
category_matcher = re.compile('.*[.]com/(.*)[.]asp')

def get_listing_data(dom):
    """
    Extract relevant data from a listing (www.daytonlocal.com/listings/*)
    :dom the document object model (web page) to extract data from
    """
    entry = dom.cssselect('div.vcard')[0]
    post = {
            'name': entry.cssselect('.fn')[0].text_content(),
            'website': entry.cssselect('.fn a')[0].get('href'),
            'logo': 'http://www.daytonlocal.com'+dom.cssselect('#MainContentArea img')[0].get('src'),
            'address1': entry.cssselect('.street-address')[0].text_content(),
            'address2': entry.cssselect('.adr br')[0].tail,
            'city': entry.cssselect('.locality')[0].text_content(),
            'state': entry.cssselect('.region')[0].text_content(),
            'zip': entry.cssselect('.postal-code')[0].text_content(),
            'phone': string.strip(entry.cssselect('.clearl')[0].text_content()),
            'description': entry.cssselect('.clearl')[2].text_content(),
    }

    #social media links
    links = entry.cssselect('.clearl')[1].cssselect('a')
    for link in links:
        href = link.get('href')
        if 'facebook' in href:
            post['facebook'] = facebook_matcher.match(href).group(1)
        elif 'twitter' in href:
            post['twitter'] = twitter_matcher.match(href).group(1)
        else:
            match = category_matcher.match(href)
            if match:
                post['category'] = match.group(1).split('/')

    #Strip all strings
    for k, v in post.iteritems():
        if isinstance(v, basestring):
            post[k] = v.strip()

    return post
