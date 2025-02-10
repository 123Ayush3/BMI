import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# create the app
app = Flask(__name__)
# configure the SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_bmi():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        height = float(data.get('height', 0))
        weight = float(data.get('weight', 0))
        unit_system = data.get('unit_system', 'metric')

        if height <= 0 or weight <= 0:
            return jsonify({'error': 'Height and weight must be positive numbers'}), 400

        # Calculate BMI
        if unit_system == 'metric':
            height_m = height / 100  # convert cm to m
            bmi = weight / (height_m * height_m)
        else:  # imperial
            bmi = (weight * 703) / (height * height)

        # Determine BMI category
        if bmi < 18.5:
            category = 'Underweight'
        elif bmi < 25:
            category = 'Normal weight'
        elif bmi < 30:
            category = 'Overweight'
        else:
            category = 'Obese'

        # Save to database
        bmi_record = BMIRecord(
            height=height,
            weight=weight,
            bmi_value=bmi,
            unit_system=unit_system,
            category=category
        )
        db.session.add(bmi_record)
        db.session.commit()

        return jsonify({
            'bmi': round(bmi, 1),
            'category': category,
            'id': bmi_record.id
        })

    except Exception as e:
        app.logger.error(f"Error calculating BMI: {str(e)}")
        return jsonify({'error': 'Failed to calculate BMI. Please check your inputs.'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)