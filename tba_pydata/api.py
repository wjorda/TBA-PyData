import requests
import pandas

from multiprocessing import Pool

from tba_pydata import constants

TBA = 'https://www.thebluealliance.com/api/v3'
HEADER = {'X-TBA-Auth_Key': 'SfIaTaudX9MLcouEO0NbEktueyhKcNJ8PlBlrHuw4yXWx1D30fVQxtLHERg7QZVG'}
YEAR = 2018


def tba_fetch(path):
    resp = requests.get(TBA + path, headers=HEADER)
    print(TBA + path, resp.status_code)
    return resp.json()


def tba_fetch_many(paths, concat=True):
    pool = Pool()
    res = pool.map(tba_fetch, paths)

    if not concat:
        return res

    total = []
    for sublist in res:
        total += sublist

    return total


def status():
    res = tba_fetch('/status')
    return pandas.Series(res)


def teams(page=-1, year=None, form=None):
    if page != -1:
        if year is None:
            if form is None:
                res = tba_fetch('/teams/' + str(page))
            else:
                res = tba_fetch('/teams/%d/%s' % (page, form))
        else:
            if form is None:
                res = tba_fetch('/teams/%d/%d' % (year, page))
            else:
                res = tba_fetch('/teams/%d/%d/%s' % (year, page, form))

        if len(res) == 0:
            return None
        else:
            if form == 'keys':
                return pandas.Series(res)
            else:
                data = pandas.DataFrame(res)
    else:
        pages = range(15)
        if year is None:
            if form is None:
                paths = ('/teams/' + str(page) for page in pages)
            else:
                paths = ('/teams/%d/%s' % (page, form) for page in pages)
        else:
            if form is None:
                paths = ('/teams/%d/%d' % (year, page) for page in pages)
            else:
                paths = ('/teams/%d/%d/%s' % (year, page, form) for page in pages)

        res = tba_fetch_many(paths)
        if form == 'keys':
            return pandas.Series(res)
        else:
            data = pandas.DataFrame(res)

    champs_year = '2018' if (year is None or year < 2017) else str(year)
    data['home_championship'] = data.home_championship.apply(lambda val: val[champs_year] if val is not None else None)
    data['state_prov'] = data.state_prov.apply(lambda loc: constants.STATE_PROV_NORMALIZATION[loc])
    data.index = data['key']

    return data