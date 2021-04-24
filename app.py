import requests
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from city_exist import city_exist
from data import db_session_cities, db_session
from data.cities import City
from data.users import User
from data.games import Games
from token_vk import TOKEN, geocoder_apikey
from datetime import datetime

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 203908037)
users = {}


class Bot:
    def __init__(self, id_user):
        self.id_user = id_user
        self.rules = {}
        self.start_date = 0
        self.step = 0
        self.cities_used = []
        self.welcome()

    def send_messages(self, text, keyboard=None):
        if keyboard:
            vk.messages.send(
                user_id=self.id_user,
                message=text,
                random_id=random.randint(0, 2 ** 64),
                keyboard=keyboard.get_keyboard()
            )
        else:
            vk.messages.send(
                user_id=self.id_user,
                message=text,
                random_id=random.randint(0, 2 ** 64)
            )

    def get_new_message(self, msg):
        if self.step == 2 and msg == 'Нет':
            self.step = 3
        if msg == "Завершить игру":
            self.step = 1
            self.game_over()
            return
        if msg == "Помощь":
            self.help()
            return
        if msg == "Статистика":
            self.send_messages('Вот ваша статистика ')
            return
        if self.step > 3:
            self.queue_user(msg)
        if msg == 'Начать игру' and self.step == 1:
            self.rules.clear()
            self.new_rules()
            self.start_date = datetime.now()
        elif self.step == 2 and msg != 'Нет':
            self.step += 1
            if msg == "Длинее какого-то числа":
                text = 'Длиннее какого числа?'
                self.rules['length'] = 1
            else:
                text = "Извини, я не понял"
                self.step -= 1
            self.send_messages(text=text)
        elif self.step == 3:
            if 'length' in self.rules.keys():
                if msg.isdigit():
                    self.rules['length'] = msg
                else:
                    self.send_messages("То, что Вы написали не является числом! Попробуйте снова")
                    return
            self.step += 1
            self.send_messages(text="Принято. Начинаем! Ты первый))")

    def queue_user(self, msg):
        if "length" in self.rules.keys():
            if len(msg) < int(self.rules["length"]):
                self.send_messages(f"Вы не выполнили поставленные правила!"
                                   f" Длина города должна быть больше {self.rules['length']}."
                                   f" Попробуйте снова.")
                return
        if not self.cities_used:
            self.cities_used.append(msg[0])
        if msg in self.cities_used:
            self.send_messages('Этот город уже называли. Попробуйте снова!')
            return
        for i in self.cities_used[-1][::-1]:
            if i.lower() == msg[0].lower():
                if city_exist(msg):
                    self.send_messages(f"Действительно, такой город существует..."
                                       f" Мне на букву {msg[-1][-1].upper()}")
                    self.cities_used.append(msg)
                    self.bot_queue()
                    return
                else:
                    self.send_messages("Такого города не существует( \nПопробуй снова.")
                    if len(self.cities_used) == 1:
                        self.cities_used.clear()
                    return
        self.send_messages(
            f"Вы ошиблись слово должно начинаться с {self.cities_used[-1][-1].upper()}")

    def welcome(self):
        text = "Здраствуй! Я бот для игы в слова. Выберите действие."
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Начать игру", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Помощь", color=VkKeyboardColor.NEGATIVE)
        self.step += 1
        self.send_messages(text=text, keyboard=keyboard)

    def new_rules(self):
        text = "Добавим дополнительные правила?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Нет", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button("Длинее какого-то числа", color=VkKeyboardColor.SECONDARY)
        self.step += 1
        self.send_messages(text=text, keyboard=keyboard)

    def help(self):
        self.send_messages("Здравствуй. Это бот для игры в слова."
                           " Команды, которые ты можешь использовать при работе с ним: \n"
                           "- Начать игру\n- Завершить игру\n- Помощь")

    def game_over(self):
        db_sess = db_session.create_session()
        db_sess.add(Games(user_id=self.id_user, start_date=self.start_date, end_date=datetime.now(),
                          count_cities=len(self.cities_used)))
        db_sess.commit()
        self.send_messages('Игра закончена. До встречи)')
        self.cities_used.clear()

    def bot_queue(self):
        db_sess = db_session_cities.create_session()
        city = ""
        for i in self.cities_used[-1][::-1]:
            if 'length' in self.rules.keys():
                all_city = db_sess.query(City).filter(
                    City.name.like(f'%{i.upper() + "_" * (int(self.rules["length"]) - 1)}%')).all()
            else:
                all_city = db_sess.query(City).filter(City.name.like(f'%{i.upper()}%')).all()
            if len(all_city) > 0:
                city = random.choice(all_city).name
                while city in self.cities_used and len(all_city) > 0:
                    city = random.choice(all_city).name
            if city:
                break
        if not city:
            self.send_messages('Я не знаю городов начинающихся с этой буквы... Видимо ты выиграл;)')
            self.game_over()
            return
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": geocoder_apikey,
            "geocode": city,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        json_response = response.json()
        if not json_response["response"]["GeoObjectCollection"]["featureMember"]:
            self.bot_queue()
            return
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_longitude, toponym_lattitude = toponym["Point"]["pos"].split(" ")
        geocoder_params = {
            "apikey": geocoder_apikey,
            "geocode": ",".join([toponym_longitude, toponym_lattitude]),
            "kind": "locality",
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        json_response = response.json()
        if not json_response["response"]["GeoObjectCollection"]["featureMember"]:
            self.bot_queue()
            return
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        toponym_lc = toponym["boundedBy"]["Envelope"]["lowerCorner"]
        toponym_uc = toponym["boundedBy"]["Envelope"]["upperCorner"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        if not toponym_address.split()[-1][0] in city:
            self.bot_queue()
            return
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "l": "map",
            "spn": ",".join(
                [str(float(toponym_uc.split()[0]) - float(toponym_lc.split()[0])),
                 str(float(toponym_uc.split()[1]) - float(toponym_lc.split()[1]))]),
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_api_server, params=map_params)
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        upload = vk_api.VkUpload(vk_session)
        photo = upload.photo_messages(map_file)
        vk.messages.send(
            user_id=self.id_user,
            message=toponym_address,
            random_id=random.randint(0, 2 ** 64),
            attachment=f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
        )
        self.cities_used.append(toponym_address.split()[-1])


def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            if user_id not in users:
                db_sess = db_session.create_session()
                user = vk.users.get(user_id=user_id)
                if not db_sess.query(User.id == user_id).first():
                    db_sess.add(User(id=user_id, first_name=user[0]['first_name'],
                                     last_name=user[0]['last_name']))
                    db_sess.commit()
                users[user_id] = Bot(user_id)
            users[user_id].get_new_message(event.obj.message['text'])


if __name__ == '__main__':
    db_session.global_init('db/words.db')
    db_session_cities.global_init('db/cities.db')
    main()
