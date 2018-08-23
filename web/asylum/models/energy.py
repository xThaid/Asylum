from . import db


class Energy(db.Model):
    __tablename__ = 'energy'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, index=True, unique=True, nullable=False)
    production = db.Column(db.Integer, nullable=False)
    imports = db.Column(db.Integer, nullable=False)
    exports = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_last_rows(attributes, from_date, count):
        power_production = __class__ \
            .query.with_entities(__class__.id, *attributes) \
            .order_by(__class__.id.desc()) \
            .limit(from_date) \
            .from_self() \
            .order_by(__class__.id) \
            .limit(count) \
            .all()
        data_list = []
        for x in range(1, len(attributes) + 1):
            data_list.append([o[x] for o in power_production])
        return data_list

    def __repr__(self):
        return ('Energy<id:%i ,time: %s, production: %s, import: %s, export: %s' %
                (self.id, self.time, self.production, self.import_, self.export)) + '>'
