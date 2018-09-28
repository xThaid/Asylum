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
    def get_last_rows(from_date, count=None):
        query = __class__.query.filter(__class__.time >= from_date)

        if count is not None:
            query = query.limit(count)

        return query.all()

    def __repr__(self):
        return ('Energy<id:%i ,time: %s, production: %s, import: %s, export: %s' %
                (self.id, self.time, self.production, self.import_, self.export)) + '>'
