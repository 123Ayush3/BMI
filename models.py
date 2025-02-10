from datetime import datetime
from app import db

class BMIRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bmi_value = db.Column(db.Float, nullable=False)
    unit_system = db.Column(db.String(10), nullable=False)  # 'metric' or 'imperial'
    category = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'height': self.height,
            'weight': self.weight,
            'bmi_value': self.bmi_value,
            'unit_system': self.unit_system,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }
