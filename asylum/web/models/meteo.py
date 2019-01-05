from . import db


class Meteo(db.Model):
    __tablename__ = 'meteo'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    dust_PM10 = db.Column(db.Integer, nullable=False)
    dust_PM25 = db.Column(db.Integer, nullable=False)
    dust_PM100 = db.Column(db.Integer, nullable=False)

class MeteoDaily(db.Model):
    __tablename__ = 'meteo_daily'
    id = db.Column(db.Integer, primary_key=True)
    day_ordinal = db.Column(db.Integer, nullable=False)
    temperature_min = db.Column(db.Integer, nullable=False)
    temperature_avg = db.Column(db.Integer, nullable=False)
    temperature_max = db.Column(db.Integer, nullable=False)
    humidity_min = db.Column(db.Integer, nullable=False)
    humidity_avg = db.Column(db.Integer, nullable=False)
    humidity_max = db.Column(db.Integer, nullable=False)
    pressure_min = db.Column(db.Integer, nullable=False)
    pressure_avg = db.Column(db.Integer, nullable=False)
    pressure_max = db.Column(db.Integer, nullable=False)
    dust_PM10_min = db.Column(db.Integer, nullable=False)
    dust_PM10_avg = db.Column(db.Integer, nullable=False)
    dust_PM10_max = db.Column(db.Integer, nullable=False)
    dust_PM25_min = db.Column(db.Integer, nullable=False)
    dust_PM25_avg = db.Column(db.Integer, nullable=False)
    dust_PM25_max = db.Column(db.Integer, nullable=False)
    dust_PM100_min = db.Column(db.Integer, nullable=False)
    dust_PM100_avg = db.Column(db.Integer, nullable=False)
    dust_PM100_max = db.Column(db.Integer, nullable=False)
