import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import asyncio
from config import bot_token, my_id
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler
#from gamelogic import set_scheduled_jobs

#Создание объекта бота.

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

#Описание команд для меню бота.
async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("выбрать питомца", "Выбрать питомца"),
        types.BotCommand("админу", "Написать админу"),
    ])



#Основные команды бота: start, help, выбрать питомца и написать админу.

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЭто тамагочи-бот, основанный на полезных советах по уходу за реальными питомцами. \
Заведите питомца с помощью команды '/выбрать питомца'!")

def get_first_keyboard():
    # Генерация клавиатуры.
    buttons = [
        types.InlineKeyboardButton(text="Кот", callback_data="cat"),
        types.InlineKeyboardButton(text="Не кот", callback_data="none")
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard
    
@dp.message_handler(commands=['выбрать'])
async def process_start_command(message: types.Message):
    await message.reply("Выберите одного из питомцев. Одновременно в чате может жить только один. \
        Если у вас уже есть питомец в этом чате, создание нового удалит все данные о старом!", reply_markup=get_first_keyboard())


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Это бот, в котором вы можете завести виртуального питомца, \
        действия и уход за которым будут основаны на проверенных источниках.  \
        \nДля того, чтобы завести виртуального питомца используйте команду '/выбрать'.\
        \nЕсли вам есть что спросить или сказать, напишите мне @greeensun. \
        \nТакже вы можете использовать команду '/админу' и написать сразу после нее то, что вам нужно.")

@dp.message_handler(commands=['админу'])
async def to_admin(msg: types.Message):
    await bot.send_message(my_id, msg.text + " from " + str(msg.chat.id))

#Обработка коллбеков с inline кнопок и добавление записей в бд

@dp.callback_query_handler(text="cat")
async def catcall(call: types.CallbackQuery):
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO users(chat_id, pet_type) VALUES("{call.message.chat.id}","cat")')
    conn.commit()
    await call.message.answer("Поздравляю, у вас появился кот! Не смотря на то, что существует он только в \
виртуальном пространстве, позаботьтесь о нем. Сейчас он абсолютно здоров, \
но немного проголодался.")



scheduler = AsyncIOScheduler()


# Создаем функцию, в которой будет происходить запуск наших тасков.
def set_scheduled_jobs(scheduler, bot):
    # Добавляем задачи на выполнение
    scheduler.add_job(dbmin1, "interval", minutes = 60, args=(bot,))
    #minutes = 60

    # scheduler.add_job(some_other_regular_task, "interval", seconds=100)


async def dbmin1(bot: bot):
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    cur.execute(f'SELECT chat_id from users')
    records = cur.fetchall()
    reccl =[]

    for rec in records:
        reccl.append(rec[0])

    for chat in reccl:

        conn = sqlite3.connect('db.db')
        cur = conn.cursor()
        cur.execute(f'UPDATE users SET hunger = hunger - 1 WHERE chat_id = ?',(chat,))
        conn.commit()
        cur.execute(f'SELECT hunger from users WHERE chat_id = ?',(chat,))   
        hunger = cur.fetchall()

        hung = hunger[0]
        hun = hung[0]

        if hun < 0:
            await bot.send_message(text="Питомец голоден", chat_id=chat)
            cur.execute(f'UPDATE users SET hp = hp - 1 WHERE chat_id = ?',(chat,))
            conn.commit()
            cur.execute(f'UPDATE users SET mood = mood - 1 WHERE chat_id = ?',(chat,))
            conn.commit()
        
        cur.execute(f'UPDATE users SET hunger = hunger - 1 WHERE chat_id = ?',(chat,))
        conn.commit()
        cur.execute(f'SELECT hp from users WHERE chat_id = ?',(chat,))   
        hp = cur.fetchall()

        hp1 = hp[0]
        hp2 = hp1[0]

        if hp2 < 0:
            await bot.send_message(text="Питомец мертв. Вы можете завести нового, но, будте внимательнее!", chat_id=chat)
            cur.execute(f'DELETE from users chat_id = ?',(chat,))
            conn.commit()



#Запуск long polling для контакта с серверами Telegram.

if __name__ == '__main__':

    set_scheduled_jobs(scheduler, bot)
    scheduler.start()
    executor.start_polling(dp)
