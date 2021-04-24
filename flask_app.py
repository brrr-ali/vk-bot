from flask import Flask, render_template
from data.games import Games
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/<id_user>')
def table_game(id_user):
    db_sess = db_session.create_session()
    n = db_sess.query(Games).filter(Games.user_id == id_user).all()
    j = []
    for game in n:
        j.append([game.id, game.start_date, game.end_date, game.count_cities])
    titles = ['Id игры', 'Дата начала игры', 'Дата завершения игры',
              'Использованно городов (пользователем)']
    return render_template('table_game.html', games=j, titles=titles)


if __name__ == '__main__':
    db_session.global_init('db/words.db')
    app.run()
