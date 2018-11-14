import re
from contextlib import closing

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from matplotlib import pyplot
from requests import get
from requests.exceptions import RequestException


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


# Simple text extraction
raw_html = simple_get('https://www.gosugamers.net/dota2/rankings')
html = BeautifulSoup(raw_html, 'html.parser')


# get all the ranking
ranking = [x.text.strip() for x in html.findAll("span", {"class" : "ranking"})]


# get rank points
rank_points = [point.text.strip() for point in html.findAll("span", {"class" : "elo"})]


# Extract some data from a real estate website (check a price distribution across every district in Warsaw)
raw_html_base = simple_get('https://www.gumtree.pl/s-mieszkania-i-domy-do-wynajecia/mokotow/v1c9008l3200012p1')
html = BeautifulSoup(raw_html_base, 'html.parser')
last_page = html.findAll("div", {"class" : "pagination"})[0].findAll("a", {"class" : "last follows"})[0]["href"]
re.search("(?s:.*)\d+", last_page)
max_page = re.search("\d+", last_page)[0]

# prepare a page template
price_bag = []
page_url = "https://www.gumtree.pl/s-mieszkania-i-domy-do-wynajecia/mokotow/v1c9008l3200012p{}"
pages = [page_url.format(i + 1) for i in range(np.int(max_page))]

# extract all flat prices from the website
for page in pages:
    raw_html = simple_get(page)
    html = BeautifulSoup(raw_html, 'html.parser')
    all_prices = [price.text for price in html.findAll("span", {"class" : "amount"})]
    all_prices = ["".join(re.findall("\d+", price)) for price in all_prices]
    all_prices = list(map(int, all_prices))
    [price_bag.append(price) for price in all_prices]

mean = np.int(np.mean(price_bag))
median = np.int(np.median(price_bag))

q95 = np.int(pd.DataFrame(price_bag).quantile(0.95))
price_bag_selected = [price for price in price_bag if price < q95]

# some plot analysis
pyplot.hist(price_bag_selected, 100, (0, q95))
pyplot.title("Price distribution in Mokotow district")
pyplot.annotate('mean price: ' + np.str(mean) + ' zl', (5000, 200))
pyplot.annotate('median price: ' + np.str(median) + ' zl', (5000, 180))
pyplot.xlabel("price [zl]")
pyplot.ylabel("bin [n]")
pyplot.show()
