import requests


async def fetch(url):
    try:
        r = requests.request("GET", url=url)
    except:
        return

    try:
        data = r.json()
    except:
        data = r.text()
    return data
