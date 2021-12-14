
import logging
import asyncio
from datetime import datetime
import buttons
from aiogram import Bot, Dispatcher, executor, types
from sqlighter import SQLighter
import json
import re

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
time_update = 10
button_all_progress = KeyboardButton('Успеваемость по всем предметам')
button_one_progress = KeyboardButton('Успеваемость по одному предмету')
button_settings_progress_notification = KeyboardButton('Настройка уведомления о успеваемости')
button_settings_check_notification = KeyboardButton('Настройка уведомления о сроках сдачи')
button_settings_profile = KeyboardButton('Настройка профиля')
button_profile = KeyboardButton('Профиль')
nav = ReplyKeyboardMarkup(resize_keyboard=True)
nav.add(button_all_progress,button_one_progress)
nav.add(button_settings_progress_notification,button_settings_check_notification)
nav.add(button_settings_profile,button_profile)

# задаем уровень логов
logging.basicConfig(level=logging.INFO)
API_TOKEN = '2107473500:AAHI5Oj6WJud2CHmg2JvS7KQIYKEHzha-UU'
# инициализируем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# инициализируем соединение с БД
db = SQLighter('kursovaya.db')
answer=[["ВВЕДИТЕ ФИО","FIO"],["ВВЕДИТЕ логин","username"],["ВВЕДИТЕ пароль","password"],["Готов к работе"]]

# Команда активации подписки
@dp.message_handler(commands=['start'])
async def subscribe(message: types.Message):
    await bot.send_message(message.from_user.id,text="НАЧАЛО",reply_markup=nav)
    if(not db.user_exists(message.from_user.id)):
         # если юзера нет в базе, добавляем его
        db.add_user(message.from_user.id)
        db.add_progress(db.get_user_info(message.from_user.id)[0])
    if(db.get_user_state(message.from_user.id)<3):
        await message.answer(answer[db.get_user_state(message.from_user.id)][0])
    else:
        db.update_user_state(message.from_user.id,1000)

# Команда редактирования
@dp.message_handler(commands=['edit_profile'])
async def edit_profile(message: types.Message):
        key,value = message.get_full_command()[1].split(' ')
        db.update_user_key(message.from_user.id,key,value)
        await message.answer("Изменено")
        
@dp.message_handler()
async def default_message(message: types.Message):
        #"""Основная функция для обработки событий"""
        state = db.get_user_state(message.from_user.id)
        if(state==1):
            #"""Прохождение ввода логина"""
            login = re.compile(r'[a-z][a-z][a-z]\d\d[a-z]\d\d\d')
            if(state==1 and login.match(message.text)!=None):
                db.update_user_key(message.from_user.id,answer[state][1],message.text)
                db.update_user_state(message.from_user.id,state+1)
                await message.answer(answer[state+1][0])
            else:
               await message.answer(answer[state][0])
        elif(state==0):
            #"""Прохождение ввода ФИО"""
            db.update_user_key(message.from_user.id,answer[state][1],message.text)
            db.update_user_state(message.from_user.id,state+1)
            await message.answer(answer[state+1][0])
        elif(state==2):
            #"""Прохождение ввода пароль"""
            db.update_user_key(message.from_user.id,answer[state][1],message.text)
            db.update_user_state(message.from_user.id,state+1)
            await message.answer(answer[state+1][0])
        elif(state==3):
            #"""Прохождение изменение данных"""
            if(len(message.text.split(' '))==2):
                key,value = message.text.split(' ')
                login = re.compile(r'[a-z][a-z][a-z]\d\d[a-z]\d\d\d')
                if(key=='login'):
                    if(login.match(value)!=None):
                        db.update_user_key(message.from_user.id,key,value)
                        db.update_user_state(message.from_user.id,1000)
                        await message.answer("Изменено")
                    else:
                        await message.answer("ВВЕДИТЕ НАЗВАНИЕ ПОЛЯ КОТОРОЕ НАДО ИЗМЕНЕНИТЬ И ЗНАЧЕНИЕ НА КОТОРОЕ ИЗМЕНИТЬ")
                else:
                    try:
                        db.update_user_key(message.from_user.id,key,value)
                        db.update_user_state(message.from_user.id,1000)
                        await message.answer("Изменено")
                    except:
                        await message.answer("Что то пошло не так")
                        
            else:
                await message.answer("ВВЕДИТЕ НАЗВАНИЕ ПОЛЯ КОТОРОЕ НАДО ИЗМЕНЕНИТЬ И ЗНАЧЕНИЕ НА КОТОРОЕ ИЗМЕНИТЬ")
                
        elif(state==4):
            #"""Получение успеваемости по одному предмету"""
            subject = message.text
            try:
                str_test = db.get_data(db.get_user_info(message.from_user.id)[0])    
                db.update_user_state(message.from_user.id,1000)
                await message.answer(transform_one(json.loads(str_test),subject))
            except:
                await message.answer("Нет такого предмета")
        elif(state==5):
            #"""Получение информации о интервалах проверки"""
            if(message.text>='0' and message.text<='9'):
                db.update_user_state(message.from_user.id,1000)
                global time_update
                time_update = int(message.text)
                await message.answer("Изменено")
            else:
                await message.answer("Введите еще раз")
        elif(state==6):
            #"""Получение информации необходимой для уведомлений о сроках контрольных мероприятий"""
            if(message.text>='0' and message.text<='9'):
                db.update_user_state(message.from_user.id,1000)
                await message.answer("Изменено")
            else:
                await message.answer("Введите еще раз")
        else:
            if(message.text=="Настройка профиля"):
                await message.delete()
                db.update_user_state(message.from_user.id,3)
                await message.answer("ВВЕДИТЕ НАЗВАНИЕ ПОЛЯ КОТОРОЕ НАДО ИЗМЕНЕНИТЬ И ЗНАЧЕНИЕ НА КОТОРОЕ ИЗМЕНИТЬ")
            elif(message.text=='Успеваемость по одному предмету'):
                await message.delete()
                db.update_user_state(message.from_user.id,4)
                await message.answer("ВВЕДИТЕ НАЗВАНИЕ ПРЕДМЕТА")
            elif(message.text=='Успеваемость по всем предметам'):
                str_test = db.get_data(db.get_user_info(message.from_user.id)[0])              
                await message.answer(transform_all(json.loads(str_test)))
            elif(message.text=='Настройка уведомления о успеваемости'):
                await message.delete()
                db.update_user_state(message.from_user.id,5)
                await message.answer("ИНТЕРВАЛ МЕЖДУ ПРОВЕРКАМИ(В МИНУТАХ)")
            elif(message.text=='Настройка уведомления о сроках сдачи'):
                await message.delete()
                db.update_user_state(message.from_user.id,6)
                await message.answer("ЗА СКОЛЬКО ДНЕЙ СООБЩИТЬ?ЕСЛИ 0,то выключено")
            elif (message.text=='Профиль'):
                await message.delete()
                user_info=db.get_user_info(message.from_user.id)
                #await message.answer(user_info)
                await message.answer("ЛОГИН "+user_info[3]+"\nПАРОЛЬ "+user_info[4])
async def on_bot_start_up(dispatcher: Dispatcher) -> None:
    asyncio.create_task(scheduled(3))
def transform_all(data):
    """функция для получение успеваемости по всем предметам"""
    data_result = []
    ii=0
    str_result=""
    for row in data[1:]:
        data_result.append([row[0][0:10]+' '])
        str_result+=row[0][0:10]+' '
        for element in row[1:]:
            if(element!=""):
                if(element[0:1]=="М"):
                    data_result[ii].append(element[0:3])
                    str_result+=element[0:3]+'|'
                else:
                    data_result[ii].append(element)
                    str_result+=element+'|'

        if str_result[-1]=='|':
            str_result+="\n"
        else:
            str_result+="нет данных\n"
        ii+=1
    return str_result
def transform_one(data,key):
    '''фукция для получение конктретного предмета из списка всей успеваемости'''
    str_result=""
    for row in data[1:]:
       if(row[0][0:5]==key[0:5]):
            str_result+=row[0][0:10]+' '
            for element in row[1:]:
                if(element!=""):
                    if(element[0:1]=="М"):
                        str_result+=element[0:3]+'|'
                    else:
                        str_result+=element+'|'
            return str_result

    return "НЕТ ТАКОГО ПРЕДМЕТА"
async def scheduled(wait_for):
    '''Функция для периодической проверки успеваемости, а также сроков сдачи '''
    while True:
        global time_update
        marks = db.get_all_mark()
        for row in marks:
            if(row[3]==1):
                userid = db.get_user_id_from_id(row[2])
                print(row[2])
                db.set_state_mark(row[2])
                await bot.send_message(userid, 'ПРОВЕРЬТЕ ОЦЕНКИ')
        await asyncio.sleep(time_update)
        
# запускаем лонг поллинг(циркл обработки событий)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_bot_start_up)
