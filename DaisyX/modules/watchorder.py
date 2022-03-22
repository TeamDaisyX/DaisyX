import requests

from DaisyX.services.pyrogram import pbot
from pyrogram import filters
from bs4 import BeautifulSoup

@pbot.on_message(filters.command('watchorder'))

def watchorderx(_,message):
	anime =  message.text.replace(message.text.split(' ')[0], '')
	res = requests.get(f'https://chiaki.site/?/tools/autocomplete_series&term={anime}').json()
	data = None
	id_ = res[0]['id']
	res_ = requests.get(f'https://chiaki.site/?/tools/watch_order/id/{id_}').text
	soup = BeautifulSoup(res_ , 'html.parser')
	anime_names = soup.find_all('span' , class_='wo_title')
	for x in anime_names:
		if data:
			data = f"{data}\n{x.text}"
		else:
			data = x.text
	message.reply_text(f'Watchorder of {anime}: \n```{data}```')
