from . import db


class EnergyProduction(db.Model):
    __tablename__ = 'energy_production'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, index=True, unique=True, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    energy = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('<ProductionID:%i ,Energy: %s, Power: %s' % (self.id, self.energy, self.power)) + '>'


class EnergyConsumption(db.Model):
    __tablename__ = 'energy_consumption'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(64), index=True, unique=True, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    energy = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('<ConsumptionID:%i ,Energy: %s, Power: %s' % (self.id, self.energy, self.power)) + '>'
