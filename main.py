from aiogram import Bot, Dispatcher, executor
from aiogram.types import ParseMode
from aiogram.types import (
	InlineQuery, CallbackQuery,
	InlineQueryResultArticle, InputTextMessageContent,
	InlineKeyboardMarkup, InlineKeyboardButton
)

import hashlib

from src import config
from src.logic import *


bot = Bot(config.TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
dp = Dispatcher(bot)


@dp.inline_handler()
async def inline(inl: InlineQuery):
	text = inl.query or "game"
	result_id = hashlib.md5(text.encode()).hexdigest()

	keyboard = [
		[
			InlineKeyboardButton(" 🔴 ", callback_data='red_team'),
			InlineKeyboardButton(" 🔵 ", callback_data='blue_team')
   		],
		[
			InlineKeyboardButton("Играть", callback_data='play')
		]
	]

	markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

	articles = [
		InlineQueryResultArticle(
			id=result_id,
			title="The Castle Game",
			input_message_content=InputTextMessageContent("""
***__The Castle Game__***

***Игроки:***
    🔴
    🔵

***Выбор команды:***
			"""),
			reply_markup=markup
		)
	]

	await inl.answer(articles, cache_time=1, is_personal=True)


@dp.callback_query_handler()
async def query_hand(query: CallbackQuery):
	data = query.data
	
	if data == 'play_again':
		await set_team(query, 'again')
	elif data == "play":
		await start_play(query)
	elif data.endswith("_team"):
		if data == "red_team":
			await set_team(query, 'red')
		elif data == "blue_team":
			await set_team(query, 'blue')
	else:
		await pawn_move(query)


if __name__ == '__main__':
	print("The Castle Bot started!")
	executor.start_polling(dp)