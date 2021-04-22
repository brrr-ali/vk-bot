from flask import Flask, render_template
from data.games import Games
from data.users import User
import app as bot
from data import db_session
from data import db_session_cities

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def table_game():
    j = []
    db_sess = db_session.create_session()
    for game in db_sess.query(Games).all():
        print(game.start_date, game.end_date)
        user = db_sess.query(User).filter(User.id == game.user_id).first()
        j.append([game.id, user.first_name + ' ' + user.last_name,
                  game.start_date, game.end_date, game.count_cities])

    titles = ['Id игры', 'Имя пользователя', 'Дата начала игры', 'Дата завершения игры',
              'Использованно городов (пользователем)']
    return render_template('table_game.html', games=j, titles=titles)


if __name__ == '__main__':
    db_session.global_init('db/words.db')
    db_session_cities.global_init('db/cities.db')
    # app.run(port=8080, host='127.0.0.1')
    bot.main()
