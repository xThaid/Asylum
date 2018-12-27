import datetime

from sqlalchemy import and_

from . import db


class Energy(db.Model):
    __tablename__ = 'energy'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, index=True, unique=True, nullable=False)
    production = db.Column(db.Integer, nullable=False)
    import_ = db.Column('import', db.Integer, nullable=False)
    export = db.Column(db.Integer, nullable=False)
    power_production = db.Column(db.Integer, nullable=False)
    power_import = db.Column(db.Integer, nullable=False)
    power_export = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_last_rows(from_date, to_date, limit=None, desc=False):
        query = __class__.query.filter(and_(__class__.time >= from_date, __class__.time < to_date))
        if desc:
            query = query.order_by(Energy.time.desc())
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def __repr__(self):
        return ('Energy<id:%i ,time: %s, production: %s, import: %s, export: %s' %
                (self.id, self.time, self.power_production, self.power_import, self.power_export)) + '>'


class EnergyDaily(db.Model):
    __tablename__ = 'energy_daily'
    id = db.Column(db.Integer, primary_key=True)
    day_ordinal = db.Column(db.Integer, nullable=False)
    production = db.Column(db.Integer, nullable=False)
    import_ = db.Column('import', db.Integer, nullable=False)
    export = db.Column(db.Integer, nullable=False)
    production_offset = db.Column(db.Integer, nullable=False)
    import_offset = db.Column(db.Integer, nullable=False)
    export_offset = db.Column(db.Integer, nullable=False)
    max_power_production = db.Column(db.Integer, nullable=False)
    max_power_import = db.Column(db.Integer, nullable=False)
    max_power_export = db.Column(db.Integer, nullable=False)
    max_power_consumption = db.Column(db.Integer, nullable=False)
    max_power_use = db.Column(db.Integer, nullable=False)
    max_power_store = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_last_rows(from_date, to_date):
        return __class__.query.filter(and_(__class__.day_ordinal >= from_date.toordinal(),
                                           __class__.day_ordinal <= to_date.toordinal())).all()

    def __repr__(self):
        return ('EnergyDaily<id:%i ,day: %s, production: %i' %
                (self.id, str(datetime.date.fromordinal(self.day_ordinal)), self.production)) + '>'
