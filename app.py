from flask import Flask, request, jsonify,Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv() # for Devlopment env


# Initialize the Flask app
app = Flask(__name__)

# Database configuration
# db_path=os.path.join(os.path.dirname(__file__), "students.db")
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)
migrate = Migrate(app, db)
v1 = Blueprint('v1', __name__, url_prefix='/api/v1')


# Define the Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    # email2 = db.Column(db.String(100), nullable=True, unique=False)


    def __repr__(self):
        return f"Student('{self.id}', '{self.first_name}', '{self.last_name}', '{self.age}', '{self.email}')"

# Route to get all students
@v1.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    result = []
    for student in students:
        result.append({
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'age': student.age,
            'email': student.email
        })
    return jsonify(result), 200

# Route to get a single student by ID
@v1.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get(id)
    if student:
        return jsonify({
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'age': student.age,
            'email': student.email
        }), 200
    else:
        return jsonify({'error': 'Student not found'}), 404

# Route to create a new student
@v1.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()

    # Validate input data
    if not data or not data.get('first_name') or not data.get('last_name') or not data.get('age') or not data.get('email'):
        return jsonify({'error': 'Missing required fields'}), 400

    new_student = Student(
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        email=data['email']
    )

    try:
        existing_student = Student.query.filter_by(email=data['email']).first()
        if existing_student:
            return jsonify({'error': 'A student with this email already exists'}), 409  # HTTP 409 Conflict
        if new_student.age > 100 or new_student.age <=0:
            return jsonify({'error': 'Invalid Age'}), 400
        
            
        db.session.add(new_student)
        db.session.commit()
        return jsonify({
            'id': new_student.id,
            'first_name': new_student.first_name,
            'last_name': new_student.last_name,
            'age': new_student.age,
            'email': new_student.email
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route to update a student's information
@v1.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()

    # Update the student fields
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'age' in data:
        student.age = data['age']
    if 'email' in data:
        existing_student = Student.query.filter_by(email=data['email']).first()
        print(existing_student)
        if existing_student:
            return jsonify({'error': 'A student with this email already exists'}), 409  # HTTP 409 Conflict
        student.email = data['email']

    try:
        db.session.commit()
        return jsonify({
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'age': student.age,
            'email': student.email
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Route to delete a student by ID
@v1.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'Status': 'OK'}), 200

# Initialize the database (run this once to create the database)
with app.app_context():
    db.create_all()

app.register_blueprint(v1)


if __name__ == '__main__':
    app.run(debug=True)
