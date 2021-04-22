from data import db_session_cities
from data.cities import City


def city_exist(city):
    db_sess = db_session_cities.create_session()
    city = db_sess.query(City).filter(City.name == city).first()
    if city:
        return True
    return False
