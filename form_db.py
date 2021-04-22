from data.cities import City
from data import db_session_cities

db_session_cities.global_init('db/cities.db')
f = open("db_cities/cities.txt", encoding='utf-8')
m = f.read().split('\n')
f.close()
db_sess = db_session_cities.create_session()
for i in range(len(m)):
    n = m[i][m[i].find(':') + 1:].replace(';', '').replace('"', '') \
        .replace("'", '').replace('_', ' ').strip()
    if len(n.split()) == 1 and n[0].isupper():
        city = City(name=n)
        db_sess.add(city)
db_sess.commit()
db_sess.close()
