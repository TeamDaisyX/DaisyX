# Part of this file Ported From William Butcher Bot :- https://github.com/thehamkercat/WilliamButcherBot/edit/dev/wbb/modules/webss.py .
# Credits to WilliamButcherBot.

import io
import re
import sys
import traceback

import time

# Extra Plugins Provided By Team Daisy X
# Ported From WilliamButcher Bot.
# All Credit Goes to WilliamButcherBot
import urllib.request
from datetime import datetime
import datetime
from typing import List
import aiohttp
import requests
from bs4 import BeautifulSoup
from countryinfo import CountryInfo
from faker import Faker
from faker.providers import internet
from PyDictionary import PyDictionary
from pyrogram import errors, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from tswift import Song
from youtubesearchpython import VideosSearch

from DaisyX.function.inlinehelper import (
    alive_function,
    arq,
    deezer_func,
    google_search_func,
    inline_help_func,
    paste_func,
    saavn_func,
    shortify,
    torrent_func,
    translate_func,
    urban_func,
    wall_func,
    webss,
)
from DaisyX.function.pluginhelpers import fetch, json_prettify
from DaisyX.services.pyrogram import pbot as app
from DaisyX.config import get_str_key
from search_engine_parser import GoogleSearch
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

OPENWEATHERMAP_ID = get_str_key("OPENWEATHERMAP_ID", "")
TIME_API_KEY = get_str_key("TIME_API_KEY", required=False)

dictionary = PyDictionary()


class AioHttp:
    @staticmethod
    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()

    @staticmethod
    async def get_text(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.text()

    @staticmethod
    async def get_raw(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.read()


__mod_name__ = "Inline"
__help__ = """
 <b> INLINE BOT SERVICE OF @DAISYXBOT </b> 
 
<i> I'm more efficient when added as group admin. By the way these commands can be used by anyone in a group via inline.</i>

<b>Syntax</b>
   @DaisyXBot [command] [query]

<b> Commands Available</b>
- alive - Check Bot's Stats.
- yt [query] - Youtube Search.
- tr [LANGUAGE_CODE] [QUERY]** - Translate Text.
- modapk [name] - Give you direct link of mod apk.
- ud [QUERY] - Urban Dictionary Query
- google [QUERY] - Google Search.
- webss [URL] - Take Screenshot Of A Website.
- bitly [URL] - Shorten A Link.
- wall [Query] - Find Wallpapers.
- pic [Query] - Find pictures.
- saavn [SONG_NAME] - Get Songs From Saavn.
- deezer [SONG_NAME] - Get Songs From Deezer.
- torrent [QUERY] - Torrent Search.
- reddit [QUERY] - Get memes from reddit.
- imdb [QUERY] - Search movies on imdb.
- spaminfo [ID] - Get spam info of the user.
- lyrics [QUERY] - Get lyrics of the song.
- math [PROBLEM] - Solves math problem.
- paste [TEXT] - Paste text on pastebin.
- define [WORD] - Get definition from Dictionary.
- synonyms [WORD] - Get synonyms from Dictionary.
- antonyms [WORD] - Get antonyms from Dictionary.
- country [QUERY] - Get Information about given country.
- cs - Gathers Cricket info (Globally).
- covid [COUNTRY] - Get covid updates of given country.
- fakegen - Gathers fake information.
- weather [QUERY] - Get weather information.
- datetime [QUERY] - Get Date & time information of given country/region.
- app [QUERY] - Search for apps in playstore.
- gh [QUERY] - Search github.
- so [QUERY] - Search stack overflow.
"""

__MODULE__ = "Inline"
__HELP__ = """
 ==>> **INLINE BOT SERVICE OF @DAISYXBOT** <<==
`I'm more efficient when added as group admin. By the way these commands can be used by anyone in a group via inline.`

   >> Syntax <<
@DaisyXBot [command] [query]

   >> Commands Available <<
- **alive** - __Check Bot's Stats.__
- **yt [query]** - __Youtube Search.__
- **tr [LANGUAGE_CODE] [QUERY]** - __Translate Text.__
- **ud [QUERY]** - __Urban Dictionary Query.__
- **google [QUERY]** - __Google Search.__
- **modapk [name]** - __Give you direct link of mod apk__
- **webss [URL]** - __Take Screenshot Of A Website.__
- **bitly [URL]** - __Shorten A Link.__
- **wall [Query]** - __Find Wallpapers.__
- **pic [Query]** - __Find pictures.__
- **saavn [SONG_NAME]** - __Get Songs From Saavn.__
- **deezer [SONG_NAME]** - __Get Songs From Deezer.__
- **torrent [QUERY]** - __Torrent Search.__
- **reddit [QUERY]** - __Get memes from redit.__
- **imdb [QUERY]** - __Search movies on imdb.__
- **spaminfo [id]** - __Get spam info of the user.__
- **lyrics [QUERY]** - __Get lyrics of given song.__
- **math [PROBLEM]** - __Solves math problem.__
- **paste [TEXT]** - __Paste text on pastebin.__
- **define [WORD]** - __Get definition from Dictionary.__
- **synonyms [WORD]** - __Get synonyms from Dictionary.__
- **antonyms [WORD]** - __Get antonyms from Dictionary.__
- **country [QUERY]** - __Get Information about given country.__
- **cs** - __Gathers Cricket info (Globally).__
- **covid [COUNTRY]** - __Get covid updates of given country.__
- **fakegen** - __Gathers fake information.__
- **weather [QUERY]** - __Get weather information.__
- **datetime [QUERY]** - __Get Date & time information of given country/region.__
- **app [QUERY]** - __Search for apps on playstore.
- **gh [QUERY]** - __Search github.__
- **so [QUERY]** - __Search stack overfolw.__
"""


@app.on_message(filters.command("inline"))
async def inline_help(_, message):
    await app.send_message(message.chat.id, text=__HELP__)


@app.on_inline_query()
async def inline_query_handler(client, query):
    try:
        text = query.query.lower()
        answers = []
        if text.strip() == "":
            answerss = await inline_help_func(__HELP__)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
            return
        elif text.split()[0] == "alive":
            answerss = await alive_function(answers)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif text.split()[0] == "tr":
            lang = text.split()[1]
            tex = text.split(None, 2)[2]
            answerss = await translate_func(answers, lang, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif text.split()[0] == "ud":
            tex = text.split(None, 1)[1]
            answerss = await urban_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif text.split()[0] == "google":
            tex = text.split(None, 1)[1]
            answerss = await google_search_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif text.split()[0] == "webss":
            tex = text.split(None, 1)[1]
            answerss = await webss(tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)
        elif text.split()[0] == "bitly":
            tex = text.split(None, 1)[1]
            answerss = await shortify(tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "yt":
            answers = []
            search_query = text.split(None, 1)[1]
            search_query = query.query.lower().strip().rstrip()

            if search_query == "":
                await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="Type a YouTube video name...",
                    switch_pm_parameter="help",
                    cache_time=0,
                )
            else:
                search = VideosSearch(search_query, limit=50)

                for result in search.result()["result"]:
                    answers.append(
                        InlineQueryResultArticle(
                            title=result["title"],
                            description="{}, {} views.".format(
                                result["duration"], result["viewCount"]["short"]
                            ),
                            input_message_content=InputTextMessageContent(
                                "https://www.youtube.com/watch?v={}".format(
                                    result["id"]
                                )
                            ),
                            thumb_url=result["thumbnails"][0]["url"],
                        )
                    )

                try:
                    await query.answer(results=answers, cache_time=0)
                except errors.QueryIdInvalid:
                    await query.answer(
                        results=answers,
                        cache_time=0,
                        switch_pm_text="Error: Search timed out",
                        switch_pm_parameter="",
                    )

        elif text.split()[0] == "wall":
            tex = text.split(None, 1)[1]
            answerss = await wall_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "pic":
            tex = text.split(None, 1)[1]
            answerss = await wall_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "saavn":
            tex = text.split(None, 1)[1]
            answerss = await saavn_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "deezer":
            tex = text.split(None, 1)[1]
            answerss = await deezer_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss)

        elif text.split()[0] == "torrent":
            tex = text.split(None, 1)[1]
            answerss = await torrent_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif text.split()[0] == "modapk":
            sgname = text.split(None, 1)[1]
            PabloEscobar = (
                f"https://an1.com/tags/MOD/?story={sgname}&do=search&subaction=search"
            )
            r = requests.get(PabloEscobar)
            results = []
            soup = BeautifulSoup(r.content, "html5lib")
            mydivs = soup.find_all("div", {"class": "search-results"})
            Pop = soup.find_all("div", {"class": "title"})
            cnte = len(mydivs)
            for cnt in range(cnte):
                sucker = mydivs[cnt]
                pH9 = sucker.find("a").contents[0]
                file_name = pH9
                pH = sucker.findAll("img")
                imme = pH[0]["src"]
                Pablo = Pop[0].a["href"]
                ro = requests.get(Pablo)
                soupe = BeautifulSoup(ro.content, "html5lib")
                myopo = soupe.find_all("div", {"class": "item"})
                capt = f"**{file_name}** \n** {myopo[0].text}**\n**{myopo[1].text}**\n**{myopo[2].text}**\n**{myopo[3].text}**"
                mydis0 = soupe.find_all("a", {"class": "get-product"})
                Lol9 = mydis0[0]
                lemk = "https://an1.com" + Lol9["href"]
                rr = requests.get(lemk)
                soup = BeautifulSoup(rr.content, "html5lib")
                script = soup.find("script", type="text/javascript")
                leek = re.search(r'href=[\'"]?([^\'" >]+)', script.text).group()
                dl_link = leek[5:]

                results.append(
                    InlineQueryResultPhoto(
                        photo_url=imme,
                        title=file_name,
                        caption=capt,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("Download Link", url=lemk)],
                                [
                                    InlineKeyboardButton(
                                        "Direct Download Link", url=dl_link
                                    )
                                ],
                            ]
                        ),
                    )
                )

            await client.answer_inline_query(query.id, cache_time=0, results=results)
        elif text.split()[0] == "reddit":
            subreddit = text.split(None, 1)[1]
            results = []
            reddit = await arq.reddit(subreddit)
            sreddit = reddit.subreddit
            title = reddit.title
            image = reddit.url
            link = reddit.postLink
            caption = f"""**Title:** `{title}`
            Subreddit: `{sreddit}`"""
            results.append(
                InlineQueryResultPhoto(
                    photo_url=image,
                    title="Meme Search",
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("PostLink", url=link)],
                        ]
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)

        elif text.split()[0] == "imdb":
            movie_name = text.split(None, 1)[1]
            results = []
            remove_space = movie_name.split(" ")
            final_name = "+".join(remove_space)
            page = requests.get(
                "https://www.imdb.com/find?ref_=nv_sr_fn&q=" + final_name + "&s=all"
            )
            str(page.status_code)
            soup = BeautifulSoup(page.content, "lxml")
            odds = soup.findAll("tr", "odd")
            mov_title = odds[0].findNext("td").findNext("td").text
            mov_link = (
                "http://www.imdb.com/" + odds[0].findNext("td").findNext("td").a["href"]
            )
            page1 = requests.get(mov_link)
            soup = BeautifulSoup(page1.content, "lxml")
            if soup.find("div", "poster"):
                poster = soup.find("div", "poster").img["src"]
            else:
                poster = ""
            if soup.find("div", "title_wrapper"):
                pg = soup.find("div", "title_wrapper").findNext("div").text
                mov_details = re.sub(r"\s+", " ", pg)
            else:
                mov_details = ""
            credits = soup.findAll("div", "credit_summary_item")
            if len(credits) == 1:
                director = credits[0].a.text
                writer = "Not available"
                stars = "Not available"
            elif len(credits) > 2:
                director = credits[0].a.text
                writer = credits[1].a.text
                actors = []
                for x in credits[2].findAll("a"):
                    actors.append(x.text)
                actors.pop()
                stars = actors[0] + "," + actors[1] + "," + actors[2]
            else:
                director = credits[0].a.text
                writer = "Not available"
                actors = []
                for x in credits[1].findAll("a"):
                    actors.append(x.text)
                actors.pop()
                stars = actors[0] + "," + actors[1] + "," + actors[2]
            if soup.find("div", "inline canwrap"):
                story_line = soup.find("div", "inline canwrap").findAll("p")[0].text
            else:
                story_line = "Not available"
            info = soup.findAll("div", "txt-block")
            if info:
                mov_country = []
                mov_language = []
                for node in info:
                    a = node.findAll("a")
                    for i in a:
                        if "country_of_origin" in i["href"]:
                            mov_country.append(i.text)
                        elif "primary_language" in i["href"]:
                            mov_language.append(i.text)
            if soup.findAll("div", "ratingValue"):
                for r in soup.findAll("div", "ratingValue"):
                    mov_rating = r.strong["title"]
            else:
                mov_rating = "Not available"
            lol = f"Movie - {mov_title}\n Click to see more"
            msg = (
                "<a href=" + poster + ">&#8203;</a>"
                "<b>Title : </b><code>"
                + mov_title
                + "</code>\n<code>"
                + mov_details
                + "</code>\n<b>Rating : </b><code>"
                + mov_rating
                + "</code>\n<b>Country : </b><code>"
                + mov_country[0]
                + "</code>\n<b>Language : </b><code>"
                + mov_language[0]
                + "</code>\n<b>Director : </b><code>"
                + director
                + "</code>\n<b>Writer : </b><code>"
                + writer
                + "</code>\n<b>Stars : </b><code>"
                + stars
                + "</code>\n<b>IMDB Url : </b>"
                + mov_link
                + "\n<b>Story Line : </b>"
                + story_line
            )
            results.append(
                InlineQueryResultArticle(
                    title="Imdb Search",
                    description=lol,
                    input_message_content=InputTextMessageContent(
                        msg, disable_web_page_preview=False, parse_mode="HTML"
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)
        elif text.split()[0] == "spaminfo":
            cmd = text.split(None, 1)[1]
            results = []
            url = f"https://api.intellivoid.net/spamprotection/v1/lookup?query={cmd}"
            a = await AioHttp().get_json(url)
            response = a["success"]
            if response is True:
                date = a["results"]["last_updated"]
                stats = f"**◢ Intellivoid• SpamProtection Info**:\n"
                stats += f' • **Updated on**: `{datetime.fromtimestamp(date).strftime("%Y-%m-%d %I:%M:%S %p")}`\n'
                stats += f" • **Chat Info**: [Link](t.me/SpamProtectionBot/?start=00_{cmd})\n"

                if a["results"]["attributes"]["is_potential_spammer"] is True:
                    stats += f" • **User**: `USERxSPAM`\n"
                elif a["results"]["attributes"]["is_operator"] is True:
                    stats += f" • **User**: `USERxOPERATOR`\n"
                elif a["results"]["attributes"]["is_agent"] is True:
                    stats += f" • **User**: `USERxAGENT`\n"
                elif a["results"]["attributes"]["is_whitelisted"] is True:
                    stats += f" • **User**: `USERxWHITELISTED`\n"

                stats += f' • **Type**: `{a["results"]["entity_type"]}`\n'
                stats += f' • **Language**: `{a["results"]["language_prediction"]["language"]}`\n'
                stats += f' • **Language Probability**: `{a["results"]["language_prediction"]["probability"]}`\n'
                stats += f"**Spam Prediction**:\n"
                stats += f' • **Ham Prediction**: `{a["results"]["spam_prediction"]["ham_prediction"]}`\n'
                stats += f' • **Spam Prediction**: `{a["results"]["spam_prediction"]["spam_prediction"]}`\n'
                stats += f'**Blacklisted**: `{a["results"]["attributes"]["is_blacklisted"]}`\n'
                if a["results"]["attributes"]["is_blacklisted"] is True:
                    stats += f' • **Reason**: `{a["results"]["attributes"]["blacklist_reason"]}`\n'
                    stats += f' • **Flag**: `{a["results"]["attributes"]["blacklist_flag"]}`\n'
                stats += f'**PTID**:\n`{a["results"]["private_telegram_id"]}`\n'
                results.append(
                    InlineQueryResultArticle(
                        title="Spam Info",
                        description="Search Users spam info",
                        input_message_content=InputTextMessageContent(
                            stats, disable_web_page_preview=True
                        ),
                    )
                )
                await client.answer_inline_query(
                    query.id, cache_time=0, results=results
                )
        elif text.split()[0] == "lyrics":
            cmd = text.split(None, 1)[1]
            results = []

            song = ""
            song = Song.find_song(cmd)
            if song:
                if song.lyrics:
                    reply = song.format()
                else:
                    reply = "Couldn't find any lyrics for that song! try with artist name along with song if still doesnt work try `.glyrics`"
            else:
                reply = "lyrics not found! try with artist name along with song if still doesnt work try `.glyrics`"

            if len(reply) > 4095:
                reply = "lyrics too big, Try using /lyrics"

            results.append(
                InlineQueryResultArticle(
                    title="Song Lyrics",
                    description="Click here to see lyrics",
                    input_message_content=InputTextMessageContent(
                        reply, disable_web_page_preview=False
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)
        elif text.split()[0] == "math":
            lel = text.split(None, 1)[1]
            results = []
            cmd = lel
            old_stderr = sys.stderr
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()
            redirected_error = sys.stderr = io.StringIO()
            stdout, stderr, exc = None, None, None
            san = f"print({cmd})"
            try:
                await aexec(san, client)
            except Exception:
                exc = traceback.format_exc()
            stdout = redirected_output.getvalue()
            stderr = redirected_error.getvalue()
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            evaluation = ""
            if exc:
                evaluation = exc
            elif stderr:
                evaluation = stderr
            elif stdout:
                evaluation = stdout
            else:
                evaluation = "Sorry Daisy can't find result for the given equation"
            final_output = "**EQUATION**: `{}` \n\n **SOLUTION**: \n`{}` \n".format(
                cmd, evaluation
            )
            results.append(
                InlineQueryResultArticle(
                    title="Math Problem Solved",
                    description=f"Solution - {evaluation} \nClick to see more",
                    input_message_content=InputTextMessageContent(
                        final_output, disable_web_page_preview=False
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)
        elif text.split()[0] == "paste":
            tex = text.split(None, 1)[1]
            answerss = await paste_func(answers, tex)
            await client.answer_inline_query(query.id, results=answerss, cache_time=2)

        elif text.split()[0] == "covid":
            lel = text.split(None, 1)[1]
            results = []
            country = lel.replace(" ", "")
            data = await fetch(f"https://corona.lmao.ninja/v2/countries/{country}")
            data = await json_prettify(data)
            results.append(
                InlineQueryResultArticle(
                    title="Covid Info Gathered succesfully",
                    description=data,
                    input_message_content=InputTextMessageContent(
                        data, disable_web_page_preview=False
                    ),
                )
            )
            await client.answer_inline_query(query.id, results=results, cache_time=2)
        elif text.split()[0] == "country":
            lel = text.split(None, 1)[1]
            results = []
            country = CountryInfo(lel)
            try:
                a = country.info()
            except:
                a = "Country Not Avaiable Currently"
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
        <b>
        Country Name:- {name}
        Alternative Spellings:- {hu}
        Country Area:- {area} square kilometers
        Borders:- {borders}
        Calling Codes:- {call}
        Country's Capital:- {capital}
        Country's currency:- {currencies}
        Demonym:- {HmM}
        Country Type:- {EsCoBaR}
        ISO Names:- {iso}
        Languages:- {lMAO}
        Native Name:- {nonive}
        population:- {waste}
        Region:- {reg}
        Sub Region:- {sub}
        Time Zones:- {tom}
        Top Level Domain:- {lanester}
        wikipedia:- {wiki}</b>
        Gathered By Daisy X.</b>
        """
            results.append(
                InlineQueryResultArticle(
                    title=f"Infomation of {name}",
                    description=f"""
        Country Name:- {name}
        Alternative Spellings:- {hu}
        Country Area:- {area} square kilometers
        Borders:- {borders}
        Calling Codes:- {call}
        Country's Capital:- {capital}
        
        Touch for more info
        """,
                    input_message_content=InputTextMessageContent(
                        caption, parse_mode="HTML", disable_web_page_preview=True
                    ),
                )
            )
            await client.answer_inline_query(query.id, results=results, cache_time=2)

        elif text.split()[0] == "fakegen":
            results = []
            fake = Faker()
            name = str(fake.name())
            fake.add_provider(internet)
            address = str(fake.address())
            ip = fake.ipv4_private()
            cc = fake.credit_card_full()
            email = fake.ascii_free_email()
            job = fake.job()
            android = fake.android_platform_token()
            pc = fake.chrome()
            res = f"<b><u> Fake Information Generated</b></u>\n<b>Name :-</b><code>{name}</code>\n\n<b>Address:-</b><code>{address}</code>\n\n<b>IP ADDRESS:-</b><code>{ip}</code>\n\n<b>credit card:-</b><code>{cc}</code>\n\n<b>Email Id:-</b><code>{email}</code>\n\n<b>Job:-</b><code>{job}</code>\n\n<b>android user agent:-</b><code>{android}</code>\n\n<b>Pc user agent:-</b><code>{pc}</code>"
            results.append(
                InlineQueryResultArticle(
                    title="Fake infomation gathered",
                    description="Click here to see them",
                    input_message_content=InputTextMessageContent(
                        res, parse_mode="HTML", disable_web_page_preview=True
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)

        elif text.split()[0] == "cs":
            results = []
            score_page = "http://static.cricinfo.com/rss/livescores.xml"
            page = urllib.request.urlopen(score_page)
            soup = BeautifulSoup(page, "html.parser")
            result = soup.find_all("description")
            Sed = ""
            for match in result:
                Sed += match.get_text() + "\n\n"
            res = f"<b><u>Match information gathered successful</b></u>\n\n\n<code>{Sed}</code>"
            results.append(
                InlineQueryResultArticle(
                    title="Match information gathered",
                    description="Click here to see them",
                    input_message_content=InputTextMessageContent(
                        res, parse_mode="HTML", disable_web_page_preview=False
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)

        elif text.split()[0] == "antonyms":
            results = []
            lel = text.split(None, 1)[1]
            word = f"{lel}"
            let = dictionary.antonym(word)
            set = str(let)
            jet = set.replace("{", "")
            net = jet.replace("}", "")
            got = net.replace("'", "")
            results.append(
                InlineQueryResultArticle(
                    title=f"antonyms for {lel}",
                    description=got,
                    input_message_content=InputTextMessageContent(
                        got, disable_web_page_preview=False
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)

        elif text.split()[0] == "synonyms":
            results = []
            lel = text.split(None, 1)[1]
            word = f"{lel}"
            let = dictionary.synonym(word)
            set = str(let)
            jet = set.replace("{", "")
            net = jet.replace("}", "")
            got = net.replace("'", "")
            results.append(
                InlineQueryResultArticle(
                    title=f"antonyms for {lel}",
                    description=got,
                    input_message_content=InputTextMessageContent(
                        got, disable_web_page_preview=False
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)

        elif text.split()[0] == "define":
            results = []
            lel = text.split(None, 1)[1]
            word = f"{lel}"
            let = dictionary.meaning(word)
            set = str(let)
            jet = set.replace("{", "")
            net = jet.replace("}", "")
            got = net.replace("'", "")
            results.append(
                InlineQueryResultArticle(
                    title=f"Definition for {lel}",
                    description=got,
                    input_message_content=InputTextMessageContent(
                        got, disable_web_page_preview=False
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)
            
        elif text.split()[0] == "weather":
            results = []
            sample_url = ("https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric")
            input_str = text.split(None, 1)[1]
            async with aiohttp.ClientSession() as session:
                response_api_zero = await session.get(
                    sample_url.format(input_str, OPENWEATHERMAP_ID)
                )
            response_api = await response_api_zero.json()
            if response_api["cod"] == 200:
                country_code = response_api["sys"]["country"]
                country_time_zone = int(response_api["timezone"])
                sun_rise_time = int(response_api["sys"]["sunrise"]) + country_time_zone
                sun_set_time = int(response_api["sys"]["sunset"]) + country_time_zone
                lol = (
                    """ 
        WEATHER INFO GATHERED
        Location: {}
        Temperature ☀️: {}°С
            minimium: {}°С
            maximum : {}°С
        Humidity 🌤**: {}%
        Wind 💨: {}m/s
        Clouds ☁️: {}hpa
        Sunrise 🌤: {} {}
        Sunset 🌝: {} {}""".format(
                        input_str,
                        response_api["main"]["temp"],
                        response_api["main"]["temp_min"],
                        response_api["main"]["temp_max"],
                        response_api["main"]["humidity"],
                        response_api["wind"]["speed"],
                        response_api["clouds"]["all"],
                        # response_api["main"]["pressure"],
                        time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sun_rise_time)),
                        country_code,
                        time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sun_set_time)),
                        country_code,
                    )
                )            
                results.append(
                    InlineQueryResultArticle(
                        title=f"Weather Information",
                        description=lol,
                        input_message_content=InputTextMessageContent(
                            lol, disable_web_page_preview=True
                        ),
                    )
                )
                await client.answer_inline_query(query.id, cache_time=0, results=results)      
                
        elif text.split()[0] == "datetime":
            results = []
            gay = text.split(None, 1)[1]
            lel = gay
            query_timezone = lel.lower()
            if len(query_timezone) == 2:
                result = generate_time(query_timezone, ["countryCode"])
            else:
                result = generate_time(query_timezone, ["zoneName", "countryName"])
                
            if not result:
                result = (
                    f"Timezone info not available for <b>{lel}</b>"
                )

            results.append(
                InlineQueryResultArticle(
                    title=f"Date & Time info of {lel}",
                    description=result,
                    input_message_content=InputTextMessageContent(
                        result, disable_web_page_preview=False, parse_mode="html"
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)
            
        elif text.split()[0] == "app":
            rip = []
            app_name = text.split(None, 1)[1]
            remove_space = app_name.split(" ")
            final_name = "+".join(remove_space)
            page = requests.get(
                "https://play.google.com/store/search?q=" + final_name + "&c=apps"
            )
            str(page.status_code)
            soup = BeautifulSoup(page.content, "lxml", from_encoding="utf-8")
            results = soup.findAll("div", "ZmHEEd")
            app_name = (
                results[0].findNext("div", "Vpfmgd").findNext("div", "WsMG1c nnK0zc").text
            )
            app_dev = results[0].findNext("div", "Vpfmgd").findNext("div", "KoLSrc").text
            app_dev_link = (
                "https://play.google.com"
                + results[0].findNext("div", "Vpfmgd").findNext("a", "mnKHRc")["href"]
            )
            app_rating = (
                results[0]
                .findNext("div", "Vpfmgd")
                .findNext("div", "pf5lIe")
                .find("div")["aria-label"]
            )
            app_link = (
                "https://play.google.com"
                + results[0]
                .findNext("div", "Vpfmgd")
                .findNext("div", "vU6FJ p63iDd")
                .a["href"]
            )
            app_icon = (
                results[0]
                .findNext("div", "Vpfmgd")
                .findNext("div", "uzcko")
                .img["data-src"]
            )
            app_details = "<a href='" + app_icon + "'>📲&#8203;</a>"
            app_details += " <b>" + app_name + "</b>"
            app_details += (
                "\n\n<code>Developer :</code> <a href='"
                + app_dev_link
                + "'>"
                + app_dev
                + "</a>"
            )
            app_details += "\n<code>Rating :</code> " + app_rating.replace(
                "Rated ", "⭐ "
            ).replace(" out of ", "/").replace(" stars", "", 1).replace(
                " stars", "⭐ "
            ).replace(
                "five", "5"
            )
            app_details += (
                "\n<code>Features :</code> <a href='"
                + app_link
                + "'>View in Play Store</a>"
            )
            app_details += "\n\n===> @DaisySupport_Official <==="
            rip.append(
                InlineQueryResultArticle(
                    title=f"Datails of {app_name}",
                    description=app_details,
                    input_message_content=InputTextMessageContent(
                        app_details, disable_web_page_preview=True, parse_mode="html"
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=rip)
            
        elif text.split()[0] == "gh":
            results = []
            gett = text.split(None, 1)[1]
            text = gett + ' "site:github.com"'
            gresults = await GoogleSearch().async_search(text, 1)
            result = ""
            for i in range(4):
                try:
                    title = gresults["titles"][i].replace("\n", " ")
                    source = gresults["links"][i]
                    description = gresults["descriptions"][i]
                    result += f"[{title}]({source})\n"
                    result += f"`{description}`\n\n"
                except IndexError:
                    pass
            results.append(
                InlineQueryResultArticle(
                    title=f"Results for {gett}",
                    description=f" Github info of {title}\n  Touch to read",
                    input_message_content=InputTextMessageContent(
                        result, disable_web_page_preview=True
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)
            
        elif text.split()[0] == "so":
            results = []
            gett = text.split(None, 1)[1] 
            text = gett + ' "site:stackoverflow.com"'
            gresults = await GoogleSearch().async_search(text, 1)
            result = ""
            for i in range(4):
                try:
                    title = gresults["titles"][i].replace("\n", " ")
                    source = gresults["links"][i]
                    description = gresults["descriptions"][i]
                    result += f"[{title}]({source})\n"
                    result += f"`{description}`\n\n"
                except IndexError:
                    pass
            results.append(
                InlineQueryResultArticle(
                    title=f"Stack overflow saerch - {title}",
                    description=f" Touch to view search results on {title}",
                    input_message_content=InputTextMessageContent(
                        result, disable_web_page_preview=True
                    ),
                )
            )
            await client.answer_inline_query(query.id, cache_time=0, results=results)
            

    except (IndexError, TypeError, KeyError, ValueError):
        return


async def aexec(code, client):
    exec(f"async def __aexec(client): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](client)
 

def generate_time(to_find: str, findtype: List[str]) -> str:
    data = requests.get(
        f"http://api.timezonedb.com/v2.1/list-time-zone"
        f"?key={TIME_API_KEY}"
        f"&format=json"
        f"&fields=countryCode,countryName,zoneName,gmtOffset,timestamp,dst"
    ).json()

    for zone in data["zones"]:
        for eachtype in findtype:
            if to_find in zone[eachtype].lower():
                country_name = zone["countryName"]
                country_zone = zone["zoneName"]
                country_code = zone["countryCode"]

                if zone["dst"] == 1:
                    daylight_saving = "Yes"
                else:
                    daylight_saving = "No"

                date_fmt = r"%d-%m-%Y"
                time_fmt = r"%H:%M:%S"
                day_fmt = r"%A"
                gmt_offset = zone["gmtOffset"]
                timestamp = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=gmt_offset)
                current_date = timestamp.strftime(date_fmt)
                current_time = timestamp.strftime(time_fmt)
                current_day = timestamp.strftime(day_fmt)

                break

    try:
        result = (
            f" DATE AND TIME OF COUNTRY"
            f"🌍Country :{country_name}\n"
            f"⏳Zone Name : {country_zone}\n"
            f"🗺Country Code: {country_code}\n"
            f"🌞Daylight saving : {daylight_saving}\n"
            f"🌅Day : {current_day}\n"
            f"⌚Current Time : {current_time}\n"
            f"📆Current Date :{current_date}"
        )
    except BaseException:
        result = None

    return result
