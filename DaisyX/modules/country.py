# For porting this plugin you need to add 2 things in requirements for that check requirements of this repo.


from countryinfo import CountryInfo

from DaisyX.services.events import register
from DaisyX.services.telethon import tbot as borg


@register(pattern="^/country (.*)")
async def msg(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    lol = input_str
    country = CountryInfo(lol)
    try:
        a = country.info()
    except:
        await event.reply("Country Not Avaiable Currently")
    name = a.get("name")
    bb = a.get("altSpellings")
    hu = ""
    for p in bb:
        hu += p + ",  "

    area = a.get("area")
    borders = ""
    hell = a.get("borders")
    for fk in hell:
        borders += fk + ",  "

    call = ""
    WhAt = a.get("callingCodes")
    for what in WhAt:
        call += what + "  "

    capital = a.get("capital")
    currencies = ""
    fker = a.get("currencies")
    for FKer in fker:
        currencies += FKer + ",  "

    HmM = a.get("demonym")
    geo = a.get("geoJSON")
    pablo = geo.get("features")
    Pablo = pablo[0]
    PAblo = Pablo.get("geometry")
    EsCoBaR = PAblo.get("type")
    iso = ""
    iSo = a.get("ISO")
    for hitler in iSo:
        po = iSo.get(hitler)
        iso += po + ",  "
    fla = iSo.get("alpha2")
    fla.upper()

    languages = a.get("languages")
    lMAO = ""
    for lmao in languages:
        lMAO += lmao + ",  "

    nonive = a.get("nativeName")
    waste = a.get("population")
    reg = a.get("region")
    sub = a.get("subregion")
    tik = a.get("timezones")
    tom = ""
    for jerry in tik:
        tom += jerry + ",   "

    GOT = a.get("tld")
    lanester = ""
    for targaryen in GOT:
        lanester += targaryen + ",   "

    wiki = a.get("wiki")

    caption = f"""<b><u>Information Gathered Successfully</b></u>
<b>Country Name:-</b> {name}
<b>Alternative Spellings:-</b> {hu}
<b>Country Area:-</b> {area} square kilometers
<b>Borders:-</b> {borders}
<b>Calling Codes:-</b> {call}
<b>Country's Capital:-</b> {capital}
<b>Country's currency:-</b> {currencies}
<b>Demonym:-</b> {HmM}
<b>Country Type:-</b> {EsCoBaR}
<b>ISO Names:-</b> {iso}
<b>Languages:-</b> {lMAO}
<b>Native Name:-</b> {nonive}
<b>Population:-</b> {waste}
<b>Region:-</b> {reg}
<b>Sub Region:-</b> {sub}
<b>Time Zones:-</b> {tom}
<b>Top Level Domain:-</b> {lanester}
<b>wikipedia:-</b> {wiki}

<i>Gathered By DaisyX.</i>
"""

    await borg.send_message(
        event.chat_id,
        caption,
        parse_mode="HTML",
    )
