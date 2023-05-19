from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup as bs


def search(inn):
    output = ""
    result = {}
    for key, value in parse_nalog(inn).items():
        result[key] = value
    r, contragent_id = parse_vbankcenter(inn)
    for key, value in r.items():
        result[key] = value
    for key, value in result.items():
        output += f"{value}\n"
    return output, contragent_id


def parse_nalog(inn):
    url = 'https://egrul.nalog.ru'
    url_1 = 'https://egrul.nalog.ru/search-result/'
    url_2 = 'https://egrul.nalog.ru/vyp-download/'
    try:
        r = requests.post(url, data={'query': inn})
        r1 = requests.get(url_1 + r.json()['t'])
        requests.get(url_2 + r1.json()['rows'][0]['t'])
        s = requests.Session()
        s.get(url + '/index.html')
        r = s.post(url, data={'query': inn}, cookies=s.cookies)
        r1 = s.get(url_1 + r.json()['t'], cookies=s.cookies)
        resp_json = r1.json()['rows'][0]
        result = {
            'name': resp_json['c'],
            '_1': '',
            'address': resp_json['a'],
            'gen': f"{resp_json['g']}",
            '_2': '',
            'inn': f"ИНН: {resp_json['i']}",
            'ogrn': f"ОГРН: {resp_json['o']}",
            'ogrn_date': f"Дата присвоения ОГРН: {resp_json['r']}",
            'kpp': f"КПП: {resp_json['p']}"
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        result = {}
    return result


def parse_vbankcenter(inn):
    contragent_id = ''
    try:
        url = f'https://vbankcenter.ru/contragent/search?searchStr={inn}'
        s = requests.Session()
        resp = s.get(url)
        html = bs(resp.content, "html.parser")
        href = html.select(
            "body > gweb-root > gweb-breadcrumbs-outlet > gweb-search-results > main > section > div > gweb-pageable "
            "> ul "
            "> li:nth-child(1) > div > gweb-search-results-card > article > h5 > a")[0]['href']
        url1 = f'https://vbankcenter.ru{href}'
        resp = s.get(url1)
        html = bs(resp.content, "html.parser")
        res = {'creation date': f'Дата создания: ' + html.select(
            "body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > gweb-requisites-ul > "
            "div.requisites-ul.grid.grid-cols-2.grid-rows-2.grid-flow-col.items-start.gap-x-6.gap-y-4 > "
            "div.requisites-ul-item.grid.items-start.gap-y-4.gap-x-12 > section:nth-child(1) > div:nth-child(2) > "
            "gweb-copy > span > span:nth-child(1)")[
            0].text, 'capital': 'Уставный капитал: ' + html.select(
            "body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > gweb-finanstat > "
            "gweb-finanstat-item:nth-child(1) > p")[0].text, '_3': '', '_contacts': 'Контакты:'}

        for index, contact in enumerate(
                html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div '
                            '> gweb-requisites-ul > '
                            'div.requisites-ul.grid.grid-cols-2.grid-rows-2.grid-flow-col.items'
                            '-start.gap-x-6.gap-y-4 > '
                            'div.requisites-ul-item.grid.items-start.gap-y-4.gap-x-12 > '
                            'section:nth-child(4) > div > .items-baseline')):
            res[f'contact-{index}'] = contact.text
        res['_4'] = ''
        res['arbitrazh'] = html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > '
                                       'div:nth-child(2) > div:nth-child(3) > section > gweb-arbitrages > p')[
            0].text.strip()
        res['proizvodstvo'] = \
            html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > '
                        'div:nth-child(1) > gweb-executive-proceeding > p')[0].text.strip()
        res['licences'] = html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > '
                                      'div:nth-child(1) > gweb-licenses > p')[0].text.strip()
        res['fas'] = html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > '
                                 'div:nth-child(1) > section.p-7.bg-white.rounded.order-last > gweb-rnp > p')[
            0].text.strip()

        res['_5'] = ''
        res['_checks'] = "Проверки:"
        res[
            'checks_plan'] = f'Плановые: {html.select("body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > div:nth-child(1) > div > section > gweb-checks > div.flex.flex-wrap > div:nth-child(1) > a")[0].text}'
        res[
            'checks_no_plan'] = f'Внеплановые: {html.select("body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > div:nth-child(1) > div > section > gweb-checks > div.flex.flex-wrap > div:nth-child(2) > a")[0].text}'
        res[
            'checks_breach'] = f'Нарушений: {html.select("body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > div:nth-child(1) > div > section > gweb-checks > div.flex.flex-wrap > div:nth-child(3) > a")[0].text}'
        res[
            'checks_future'] = f'Предстоит: {html.select("body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > div > div:nth-child(1) > div > section > gweb-checks > div.flex.flex-wrap > div:nth-child(4) > a")[0].text}'

        res['_6'] = ''
        res['_govcontracts'] = 'Госконтракты:'
        res['govcontracts_producer'] = \
            html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div '
                        '> div > div:nth-child(1) > section.p-7.font-normal.bg-white.rounded > '
                        'gweb-contracts > div.flex.my-2.mx-0 > '
                        'button.contracts-btn.btn.active\:text-white.text-base.rounded-r-none'
                        '.btn-primary')[0].text.strip()
        res['govcontracts_client'] = \
            html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-card > div > '
                        'div > div:nth-child(1) > section.p-7.font-normal.bg-white.rounded > '
                        'gweb-contracts > div.flex.my-2.mx-0 > '
                        'button.contracts-btn.btn.active\:text-white.text-base.rounded-l-none'
                        '.btn-outline-primary.bg-white')[0].text.strip()
        contragent_id = urlparse(url1).path.split("/")[-1]
    except Exception as e:
        print(f"An error occurred: {e}")
        res = {}
    return res, contragent_id


def search_licenses(contragent_id, page):
    if contragent_id == '':
        return
    result = []
    url = f'https://vbankcenter.ru/contragent/{contragent_id}/licenses?page={page}'
    resp = requests.get(url)
    html = bs(resp.content, "html.parser")
    elems = html.select(".pageable-content > .pageable-item")
    licenses = html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-licenses > div > '
                           'gweb-licenses-list > '
                           'section > p')[0].text.strip().split()[-1]
    if len(elems):
        for el in elems:
            res = ""
            res += f'{el.select("div > div.flex.flex-wrap.items-center.justify-between > div > p")[0].text}\n'
            res += f'{el.select(" div > div:nth-child(2)")[0].text}\n'
            res += f'{el.select(" div > div:nth-child(3)")[0].text}\n'
            res += f'{el.select(" div > div:nth-child(4)")[0].text}\n'
            result.append(res)
    return result, int(licenses)


def search_arbitrary(contragent_id, page):
    if contragent_id == '':
        return
    result = []
    url = f'https://vbankcenter.ru/contragent/{contragent_id}/arbitrages?page={page}'
    resp = requests.get(url)
    html = bs(resp.content, "html.parser")
    elems = html.select(".pageable-content > .pageable-item")
    count = html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-arbitrages > div > '
                        'gweb-company-arbitrages-list > section > '
                        'span.inline-block.mb-11.text-night-sky-300.font-normal')[0].text.strip().split()[-1]
    if len(elems):
        for el in elems:
            res = ""
            res += f'{el.select("div > gweb-company-arbitrages-item > div.flex.justify-between > div > h5")[0].text}\n'
            res += f'{el.select("div > gweb-company-arbitrages-item > div.flex.justify-between > div > span")[0].text}\n\n '
            res += f'{el.select("div > gweb-company-arbitrages-item > span")[0].text}\n'
            res += f'{el.select("div > gweb-company-arbitrages-item > div.mt-9.mb-5.font-normal")[0].text}\n'
            elem = el.select("div > gweb-company-arbitrages-item > div:nth-child(4)")
            if len(elem):
                res += f'{elem[0].text}\n'
            elem = el.select("div > gweb-company-arbitrages-item > div:nth-child(5)")
            if len(elem):
                res += f'{elem[0].text}\n'
            elem = el.select("div > gweb-company-arbitrages-item > div:nth-child(6)")
            if len(elem):
                res += f'{elem[0].text}\n'
            result.append(res)
    return result, int(count)


def search_enforcement(contragent_id, page):
    if contragent_id == '':
        return
    result = []
    url = f'https://vbankcenter.ru/contragent/{contragent_id}/fssp?page={page}'
    resp = requests.get(url)
    html = bs(resp.content, "html.parser")
    elems = html.select(".pageable-content > .pageable-item")
    count = html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-fssp > div > '
                        'gweb-company-fssp-list > section > div.mb-8 > span')[0].text.strip().split()[-1]
    if len(elems):
        for el in elems:
            res = ""
            res += f'{el.select("div > div.flex.flex-wrap.justify-between.mb-2 > div:nth-child(1) > h5")[0].text.strip()} {el.select("div > div.flex.flex-wrap.justify-between.mb-2 > div:nth-child(1) > span")[0].text.strip()}\n '
            res += f'{el.select("div > p > span:nth-child(1)")[0].text.strip()} {el.select("div > p > span:nth-child(2)")[0].text.strip()}\n '
            res += f'{el.select("div > div.flex.flex-wrap.justify-between.mb-2 > div:nth-child(2)")[0].text.strip()}\n\n'
            res += f'{el.select("div > div.flex.flex-col > div.flex.mt-3 > div > p")[0].text.strip()} {el.select("div > div.flex.flex-col > div.flex.mt-3 > div > span")[0].text.strip()}\n\n'
            res += f'{el.select("div > div.flex.flex-col > div.mr-8 > div.mb-8 > span:nth-child(1)")[0].text.strip()}\n'
            res += f'{el.select("div > div.flex.flex-col > div.mr-8 > div.mb-8 > span:nth-child(2)")[0].text.strip()}\n'
            res += f'{el.select("div > div.flex.flex-col > div.mr-8 > div:nth-child(2) > span:nth-child(1)")[0].text.strip()}\n'
            res += f'{el.select("div > div.flex.flex-col > div.mr-8 > div:nth-child(2) > span:nth-child(2)")[0].text.strip()}'
            result.append(res)
    return result, int(count)


def search_revisions(contragent_id, page):
    if contragent_id == '':
        return
    result = []
    url = f'https://vbankcenter.ru/contragent/{contragent_id}/inspections?page={page}'
    resp = requests.get(url)
    html = bs(resp.content, "html.parser")
    elems = html.select(".pageable-content > .pageable-item")
    count = html.select('body > gweb-root > gweb-breadcrumbs-outlet > gweb-company-checks > div > gweb-checks-list > '
                        'section > div.mb-5 > span')[0].text.strip().split()[-1]
    if len(elems):
        for el in elems:
            res = ""
            res += f'{el.select("div > gweb-checks-item > div.flex.items-center.justify-between > div.ml-auto > span")[0].text.strip()} {el.select("div > gweb-checks-item > div.flex.items-center.justify-between > div:nth-child(1) > h5")[0].text.strip()}\n '
            res += "Период проведения: "
            since = el.select("div > gweb-checks-item > div:nth-child(2) > span:nth-child(2)")
            to = el.select("div > gweb-checks-item > div:nth-child(2) > span:nth-child(3)")
            if len(since):
                res += f'{since[0].text.strip()}'
            if len(to):
                res += f'{to[0].text.strip()}'
            res += '\n\n'
            res += f'Адрес: {el.select("div > gweb-checks-item > div:nth-child(3) > span:nth-child(2)")[0].text.strip()}\n'

            res += f'Цель: {el.select("div > gweb-checks-item > div:nth-child(4) > span:nth-child(2)")[0].text.strip()}\n'

            res += f'Орган контроля: {el.select("div > gweb-checks-item > div:nth-child(5) > span:nth-child(2)")[0].text.strip()}\n\n'

            conclusion = el.select("div > gweb-checks-item > div:nth-child(6) > span:nth-child(2)")
            if len(conclusion):
                res += f'Результат: {conclusion[0].text.strip()}'

            result.append(res)
    return result, int(count)
