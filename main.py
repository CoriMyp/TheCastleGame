from aiogram import Bot, Dispatcher, executor
from aiogram.types import ParseMode
from aiogram.types import (
	InlineQuery, CallbackQuery,
	InlineQueryResultArticle, InputTextMessageContent,
	InlineKeyboardMarkup, InlineKeyboardButton
)

import hashlib

from src import config
from src.game import *


bot = Bot(config.TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
dp = Dispatcher(bot)


@dp.inline_handler()
async def inline(inl: InlineQuery):
	text = lambda x: f"""
***__The Castle Game {x}__***

***Игроки:***
    🔴
    🔵

***Выбор команды:***
			"""

	keyboard = lambda x: [[
		InlineKeyboardButton(" 🔴 ", callback_data=f'{x} red_team'),
		InlineKeyboardButton(" 🔵 ", callback_data=f'{x} blue_team')],
		[InlineKeyboardButton("Играть", callback_data='play')]]

	markup = lambda x: InlineKeyboardMarkup(inline_keyboard=keyboard(x))

	articles = [
		InlineQueryResultArticle(id=1, title="The Castle Game - 1x1",
			input_message_content=InputTextMessageContent(text('1x1')),
			reply_markup=markup(1)
		),
		InlineQueryResultArticle(id=2, title="The Castle Game - 2x2",
			input_message_content=InputTextMessageContent(text('2x2')),
			reply_markup=markup(2))
	]

	await inl.answer(articles, cache_time=1, is_personal=True)


@dp.callback_query_handler()
async def query_hand(query: CallbackQuery):
	data = query.data
	
	if data.endswith('play_again'):
		await set_team(query, 'again')
	elif data == "play":
		await start_play(query)

	elif data.endswith('red_team'):
		await set_team(query, 'red')
	elif data.endswith("blue_team"):
		await set_team(query, 'blue')

	else:
		await pawn_move(query)


if __name__ == '__main__':
	print("The Castle Bot started!")
	executor.start_polling(dp)