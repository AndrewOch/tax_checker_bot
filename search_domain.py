import requests
from bs4 import BeautifulSoup as bs


def search(domain):
    output = ""
    result = {}
    for key, value in parse_whois(domain).items():
        result[key] = value
    for key, value in result.items():
        output += f"{value.strip()}\n"
    return output


def parse_whois(domain):
    try:
        url = f'https://whois.ru/?domain={domain}'
        r = requests.get(url)
        html = bs(r.content, "html.parser")
        resp = html.select("body > div.wrap > div > div > div.container > div > div.row.sn-whois-reginfo > div > div > "
                           "div:nth-child(2) > pre")[0]
        infos = resp.text.split('\r\n')
        res = {}
        for key, value in enumerate(infos):
            res[key] = value
    except Exception as e:
        print(f"An error occurred: {e}")
        res = {}
    return res
