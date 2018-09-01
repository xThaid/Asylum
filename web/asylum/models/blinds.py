from . import db


class BlindsTask(db.Model):
    __tablename__ = 'blinds_task'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, index=True, nullable=False)
    device = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer,  db.ForeignKey('user.id'), nullable=True)
    schedule_id = db.Column(db.Integer, nullable=True)
    timeout = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('BlindsTask<id:%i ,time: %s, device: %s, action: %s' %
                (self.id, self.time, self.device, self.action)) + '>'


class BlindsTaskHistory(db.Model):
    __tablename__ = 'blinds_task_history'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, index=True, nullable=False)
    device = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('BlindsSchedule.id'), nullable=True)
    status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('BlindsTaskHistory<id:%i ,time: %s, device: %s, action: %s' %
                (self.id, self.time, self.device, self.action)) + '>'


class BlindsSchedule(db.Model):
    __tablename__ = 'blinds_schedule'
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Integer, nullable=False)
    hour_type = db.Column(db.Integer, nullable=False)
    time_offset = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return ('BlindsSchedule<id:%i ,device: %s, action: %s, hour_type: %s' %
                (self.id, self.device, self.action, self.hour_type)) + '>'
