from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicine_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    diabetes_type = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Patient {}>'.format(self.name)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency_days = db.Column(db.Float, nullable=False)  # How often to take (daily=1, twice daily=0.5, etc.)
    purchase_frequency_days = db.Column(db.Integer, nullable=False)  # How often to buy (30, 90, etc.)
    pills_per_purchase = db.Column(db.Integer, nullable=False)  # Number of pills bought each time
    low_stock_threshold = db.Column(db.Integer, nullable=False)  # Alert when below this number
    current_stock = db.Column(db.Integer, default=0)
    last_purchase_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref=db.backref('medicines', lazy=True))
    
    def __repr__(self):
        return '<Medicine {}>'.format(self.name)
    
    def days_until_next_purchase(self):
        if not self.last_purchase_date:
            return 0
        next_purchase = self.last_purchase_date + timedelta(days=self.purchase_frequency_days)
        return (next_purchase - datetime.utcnow()).days
    
    def is_low_stock(self):
        return self.current_stock <= self.low_stock_threshold
    
    def estimated_days_remaining(self):
        if self.current_stock <= 0:
            return 0
        return int(self.current_stock / (1 / self.frequency_days))

class PurchaseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    medicine = db.relationship('Medicine', backref=db.backref('purchases', lazy=True))
    patient = db.relationship('Patient', backref=db.backref('purchases', lazy=True))

class BloodSugar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    reading = db.Column(db.Float, nullable=False)  # Blood sugar reading in mg/dL
    reading_type = db.Column(db.String(20), nullable=False)  # fasting, post_meal, random, bedtime
    measured_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    patient = db.relationship('Patient', backref=db.backref('blood_sugar_readings', lazy=True))
    
    def __repr__(self):
        return '<BloodSugar {} mg/dL>'.format(self.reading)

def get_current_patient():
    patient_id = session.get('current_patient_id')
    if patient_id:
        return Patient.query.get(patient_id)
    return Patient.query.first()  # Default to first patient

@app.route('/')
def index():
    current_patient = get_current_patient()
    if not current_patient:
        return redirect(url_for('manage_patients'))
    
    medicines = Medicine.query.filter_by(patient_id=current_patient.id).all()
    low_stock_medicines = [m for m in medicines if m.is_low_stock()]
    patients = Patient.query.all()
    return render_template('index.html', medicines=medicines, low_stock_medicines=low_stock_medicines, 
                         current_patient=current_patient, patients=patients)

@app.route('/switch_patient/<int:patient_id>')
def switch_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    session['current_patient_id'] = patient_id
    flash('Switched to {}'.format(patient.name), 'success')
    return redirect(url_for('index'))

@app.route('/manage_patients')
def manage_patients():
    patients = Patient.query.all()
    return render_template('manage_patients.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        patient = Patient(
            name=request.form['name'],
            date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
            gender=request.form.get('gender'),
            diabetes_type=request.form.get('diabetes_type'),
            notes=request.form.get('notes')
        )
        db.session.add(patient)
        db.session.commit()
        session['current_patient_id'] = patient.id
        flash('Patient added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_patient.html')

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    current_patient = get_current_patient()
    if not current_patient:
        return redirect(url_for('manage_patients'))
        
    if request.method == 'POST':
        medicine = Medicine(
            patient_id=current_patient.id,
            name=request.form['name'],
            dosage=request.form['dosage'],
            frequency_days=float(request.form['frequency_days']),
            purchase_frequency_days=int(request.form['purchase_frequency_days']),
            pills_per_purchase=int(request.form['pills_per_purchase']),
            low_stock_threshold=int(request.form['low_stock_threshold']),
            current_stock=int(request.form.get('current_stock', 0))
        )
        db.session.add(medicine)
        db.session.commit()
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_medicine.html', current_patient=current_patient)

@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    if request.method == 'POST':
        medicine.name = request.form['name']
        medicine.dosage = request.form['dosage']
        medicine.frequency_days = float(request.form['frequency_days'])
        medicine.purchase_frequency_days = int(request.form['purchase_frequency_days'])
        medicine.pills_per_purchase = int(request.form['pills_per_purchase'])
        medicine.low_stock_threshold = int(request.form['low_stock_threshold'])
        medicine.current_stock = int(request.form['current_stock'])
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_medicine.html', medicine=medicine)

@app.route('/delete_medicine/<int:id>')
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    db.session.commit()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/record_purchase/<int:id>', methods=['GET', 'POST'])
def record_purchase(id):
    medicine = Medicine.query.get_or_404(id)
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        cost = float(request.form.get('cost', 0))
        notes = request.form.get('notes', '')
        
        purchase = PurchaseHistory(
            medicine_id=id,
            patient_id=medicine.patient_id,
            quantity=quantity,
            cost=cost,
            notes=notes
        )
        
        medicine.current_stock += quantity
        medicine.last_purchase_date = datetime.utcnow()
        
        db.session.add(purchase)
        db.session.commit()
        flash('Purchase recorded successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('record_purchase.html', medicine=medicine)

@app.route('/purchase_history')
def purchase_history():
    current_patient = get_current_patient()
    if not current_patient:
        return redirect(url_for('manage_patients'))
    
    purchases = PurchaseHistory.query.filter_by(patient_id=current_patient.id).order_by(PurchaseHistory.purchase_date.desc()).all()
    return render_template('purchase_history.html', purchases=purchases, current_patient=current_patient)

@app.route('/blood_sugar')
def blood_sugar_dashboard():
    current_patient = get_current_patient()
    if not current_patient:
        return redirect(url_for('manage_patients'))
    
    # Get recent blood sugar readings
    recent_readings = BloodSugar.query.filter_by(patient_id=current_patient.id).order_by(BloodSugar.measured_at.desc()).limit(10).all()
    
    # Get readings from last 30 days for chart
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    chart_readings = BloodSugar.query.filter_by(patient_id=current_patient.id).filter(BloodSugar.measured_at >= thirty_days_ago).order_by(BloodSugar.measured_at).all()
    
    return render_template('blood_sugar_dashboard.html', 
                         recent_readings=recent_readings, 
                         chart_readings=chart_readings,
                         current_patient=current_patient)

@app.route('/add_blood_sugar', methods=['GET', 'POST'])
def add_blood_sugar():
    current_patient = get_current_patient()
    if not current_patient:
        return redirect(url_for('manage_patients'))
        
    if request.method == 'POST':
        blood_sugar = BloodSugar(
            patient_id=current_patient.id,
            reading=float(request.form['reading']),
            reading_type=request.form['reading_type'],
            measured_at=datetime.strptime(request.form['measured_at'], '%Y-%m-%dT%H:%M') if request.form.get('measured_at') else datetime.utcnow(),
            notes=request.form.get('notes')
        )
        db.session.add(blood_sugar)
        db.session.commit()
        flash('Blood sugar reading added successfully!', 'success')
        return redirect(url_for('blood_sugar_dashboard'))
    return render_template('add_blood_sugar.html', current_patient=current_patient)

@app.route('/api/inventory_status')
def api_inventory_status():
    current_patient = get_current_patient()
    if not current_patient:
        return jsonify([])
    
    medicines = Medicine.query.filter_by(patient_id=current_patient.id).all()
    data = []
    for medicine in medicines:
        data.append({
            'id': medicine.id,
            'name': medicine.name,
            'current_stock': medicine.current_stock,
            'low_stock_threshold': medicine.low_stock_threshold,
            'is_low_stock': medicine.is_low_stock(),
            'estimated_days_remaining': medicine.estimated_days_remaining(),
            'days_until_next_purchase': medicine.days_until_next_purchase()
        })
    return jsonify(data)

@app.route('/api/blood_sugar_chart_data')
def api_blood_sugar_chart_data():
    current_patient = get_current_patient()
    if not current_patient:
        return jsonify({'readings': [], 'medicines': []})
    
    # Get blood sugar readings from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    readings = BloodSugar.query.filter_by(patient_id=current_patient.id).filter(BloodSugar.measured_at >= thirty_days_ago).order_by(BloodSugar.measured_at).all()
    
    # Get medicine intake data (we'll simulate this based on stock changes)
    medicines = Medicine.query.filter_by(patient_id=current_patient.id).all()
    
    reading_data = []
    for reading in readings:
        reading_data.append({
            'date': reading.measured_at.strftime('%Y-%m-%d %H:%M'),
            'reading': reading.reading,
            'type': reading.reading_type
        })
    
    medicine_data = []
    for medicine in medicines:
        medicine_data.append({
            'name': medicine.name,
            'frequency': medicine.frequency_days
        })
    
    return jsonify({
        'readings': reading_data,
        'medicines': medicine_data
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default patients if none exist
        if not Patient.query.first():
            default_patient = Patient(name='Patient 1', diabetes_type='Type 2')
            db.session.add(default_patient)
            db.session.commit()
    app.run(host='127.0.0.1', port=8080, debug=True)