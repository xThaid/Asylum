from . import db


class Energy(db.Model):
    __tablename__ = 'energy'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, index=True, unique=True, nullable=False)
    production = db.Column(db.Integer, nullable=False)
    import_ = db.Column(db.Integer, nullable=False)
    export = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('Energy<id:%i ,time: %s, production: %s, import: %s, export: %s' %
                (self.id, self.time, self.production, self.import_, self.export)) + '>'
