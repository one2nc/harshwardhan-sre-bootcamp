import pytest
import json
import tempfile
import os
from app import app, db, Student

URL_PREFIX="/api/v1"

@pytest.fixture
def test_app():
    """Create a test Flask application"""
    # Create a temporary database file
    db_fd, database_path = tempfile.mkstemp()
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DATABASE'] = database_path
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(database_path)


@pytest.fixture
def client(test_app):
    """Create a test client"""
    return test_app.test_client()


@pytest.fixture
def sample_student_data():
    """Sample student data for testing"""
    return {
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 20,
        'email': 'john.doe@example.com'
    }


@pytest.fixture
def another_student_data():
    """Another sample student data for testing"""
    return {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'age': 22,
        'email': 'jane.smith@example.com'
    }


@pytest.fixture
def created_student(client, sample_student_data):
    """Create a student in the database and return the response data"""
    response = client.post(f'{URL_PREFIX}/students',
                          data=json.dumps(sample_student_data),
                          content_type='application/json')
    return json.loads(response.data)


@pytest.fixture
def multiple_students(client, sample_student_data, another_student_data):
    """Create multiple students in the database"""
    students = []
    for student_data in [sample_student_data, another_student_data]:
        response = client.post(f'{URL_PREFIX}/students',
                              data=json.dumps(student_data),
                              content_type='application/json')
        students.append(json.loads(response.data))
    return students


class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    def test_healthcheck(self, client):
        """Test the healthcheck endpoint"""
        response = client.get('/healthcheck')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['Status'] == 'OK'


class TestGetStudents:
    """Test cases for getting students"""
    
    def test_get_all_students_empty(self, client):
        """Test getting all students when database is empty"""
        response = client.get(f'{URL_PREFIX}/students')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_get_all_students_with_data(self, client, multiple_students):
        """Test getting all students when database has data"""
        response = client.get(f'{URL_PREFIX}/students')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        
        # Verify the data
        emails = [student['email'] for student in data]
        assert 'john.doe@example.com' in emails
        assert 'jane.smith@example.com' in emails

    def test_get_student_by_id_success(self, client, created_student):
        """Test getting a student by ID successfully"""
        student_id = created_student['id']
        
        response = client.get(f'/api/v1/students/{student_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == student_id
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['age'] == 20
        assert data['email'] == 'john.doe@example.com'

    def test_get_student_by_id_not_found(self, client):
        """Test getting a student by ID when student doesn't exist"""
        response = client.get('/api/v1/students/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Student not found'


class TestCreateStudent:
    """Test cases for creating students"""
    
    def test_create_student_success(self, client, sample_student_data):
        """Test creating a new student successfully"""
        response = client.post(f'{URL_PREFIX}/students',
                              data=json.dumps(sample_student_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['age'] == 20
        assert data['email'] == 'john.doe@example.com'
        assert data['id'] is not None

    @pytest.mark.parametrize("missing_field", [
        'first_name', 'last_name', 'age', 'email'
    ])
    def test_create_student_missing_fields(self, client, sample_student_data, missing_field):
        """Test creating a student with missing required fields"""
        incomplete_data = sample_student_data.copy()
        del incomplete_data[missing_field]
        
        response = client.post(f'{URL_PREFIX}/students',
                              data=json.dumps(incomplete_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Missing required fields'

    def test_create_student_duplicate_email(self, client, created_student, another_student_data):
        """Test creating a student with duplicate email"""
        # Try to create second student with same email as the first
        duplicate_email_data = another_student_data.copy()
        duplicate_email_data['email'] = created_student['email']
        
        response = client.post(f'{URL_PREFIX}/students',
                              data=json.dumps(duplicate_email_data),
                              content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error'] == 'A student with this email already exists'

    def test_create_student_invalid_json(self, client):
        """Test creating a student with invalid JSON data"""
        response = client.post(f'{URL_PREFIX}/students',
                              data='invalid json',
                              content_type='application/json')
        
        assert response.status_code == 400

    def test_create_student_empty_data(self, client):
        """Test creating a student with empty data"""
        response = client.post(f'{URL_PREFIX}/students',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Missing required fields'


class TestUpdateStudent:
    """Test cases for updating students"""
    
    def test_update_student_success(self, client, created_student):
        """Test updating a student successfully"""
        student_id = created_student['id']
        update_data = {
            'first_name': 'Johnny',
            'age': 21
        }
        
        response = client.put(f'/api/v1/students/{student_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'Johnny'
        assert data['age'] == 21
        assert data['last_name'] == 'Doe'  # Should remain unchanged
        assert data['email'] == 'john.doe@example.com'  # Should remain unchanged

    def test_update_student_all_fields(self, client, created_student):
        """Test updating all fields of a student"""
        student_id = created_student['id']
        update_data = {
            'first_name': 'Jonathan',
            'last_name': 'Doe-Smith',
            'age': 25,
            'email': 'jonathan.doe.smith@example.com'
        }
        
        response = client.put(f'/api/v1/students/{student_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'Jonathan'
        assert data['last_name'] == 'Doe-Smith'
        assert data['age'] == 25
        assert data['email'] == 'jonathan.doe.smith@example.com'

    def test_update_student_not_found(self, client):
        """Test updating a student that doesn't exist"""
        update_data = {'first_name': 'Johnny'}
        
        response = client.put('/api/v1/students/999',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Student not found'

    def test_update_student_duplicate_email(self, client, multiple_students):
        """Test updating a student with an email that already exists"""
        student1_id = multiple_students[0]['id']
        student2_id = multiple_students[1]['id']
        
        # Try to update student2 with student1's email
        update_data = {
            'email': multiple_students[0]['email']
        }
        
        response = client.put(f'/api/v1/students/{student2_id}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error'] == 'A student with this email already exists'

    def test_update_student_partial_update(self, client, created_student):
        """Test partial update of a student"""
        student_id = created_student['id']
        
        # Update only the age
        response = client.put(f'/api/v1/students/{student_id}',
                             data=json.dumps({'age': 30}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['age'] == 30
        # Other fields should remain unchanged
        assert data['first_name'] == created_student['first_name']
        assert data['last_name'] == created_student['last_name']
        assert data['email'] == created_student['email']


class TestDeleteStudent:
    """Test cases for deleting students"""
    
    def test_delete_student_success(self, client, created_student):
        """Test deleting a student successfully"""
        student_id = created_student['id']
        
        response = client.delete(f'/api/v1/students/{student_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Student deleted'
        
        # Verify the student is actually deleted
        get_response = client.get(f'/api/v1/students/{student_id}')
        assert get_response.status_code == 404

    def test_delete_student_not_found(self, client):
        """Test deleting a student that doesn't exist"""
        response = client.delete('/api/v1/students/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Student not found'

    def test_delete_student_and_verify_list(self, client, multiple_students):
        """Test deleting a student and verify it's removed from the list"""
        student_to_delete = multiple_students[0]
        remaining_student = multiple_students[1]
        
        # Delete one student
        response = client.delete(f'/api/v1/students/{student_to_delete["id"]}')
        assert response.status_code == 200
        
        # Verify only one student remains
        response = client.get(f'{URL_PREFIX}/students')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['id'] == remaining_student['id']


class TestStudentModel:
    """Test cases for the Student model"""
    
    def test_student_creation(self, test_app):
        """Test creating a Student model instance"""
        with test_app.app_context():
            student = Student(
                first_name='John',
                last_name='Doe',
                age=20,
                email='john.doe@example.com'
            )
            
            db.session.add(student)
            db.session.commit()
            
            assert student.id is not None
            assert student.first_name == 'John'
            assert student.last_name == 'Doe'
            assert student.age == 20
            assert student.email == 'john.doe@example.com'

    def test_student_model_representation(self, test_app):
        """Test the Student model string representation"""
        with test_app.app_context():
            student = Student(
                first_name='John',
                last_name='Doe',
                age=20,
                email='john.doe@example.com'
            )
            db.session.add(student)
            db.session.commit()
            
            expected_repr = f"Student('{student.id}', 'John', 'Doe', '20', 'john.doe@example.com')"
            assert str(student) == expected_repr

    def test_student_email_unique_constraint(self, test_app):
        """Test that email field has unique constraint"""
        with test_app.app_context():
            student1 = Student(
                first_name='John',
                last_name='Doe',
                age=20,
                email='john.doe@example.com'
            )
            
            student2 = Student(
                first_name='Jane',
                last_name='Smith',
                age=22,
                email='john.doe@example.com'  # Same email
            )
            
            db.session.add(student1)
            db.session.commit()
            
            db.session.add(student2)
            
            # This should raise an exception due to unique constraint
            with pytest.raises(Exception):
                db.session.commit()

    def test_student_query_by_email(self, test_app):
        """Test querying student by email"""
        with test_app.app_context():
            student = Student(
                first_name='John',
                last_name='Doe',
                age=20,
                email='john.doe@example.com'
            )
            
            db.session.add(student)
            db.session.commit()
            
            # Query by email
            found_student = Student.query.filter_by(email='john.doe@example.com').first()
            assert found_student is not None
            assert found_student.first_name == 'John'
            assert found_student.last_name == 'Doe'

    def test_student_query_all(self, test_app):
        """Test querying all students"""
        with test_app.app_context():
            students_data = [
                ('John', 'Doe', 20, 'john.doe@example.com'),
                ('Jane', 'Smith', 22, 'jane.smith@example.com'),
                ('Bob', 'Johnson', 25, 'bob.johnson@example.com')
            ]
            
            for first_name, last_name, age, email in students_data:
                student = Student(
                    first_name=first_name,
                    last_name=last_name,
                    age=age,
                    email=email
                )
                db.session.add(student)
            
            db.session.commit()
            
            # Query all students
            all_students = Student.query.all()
            assert len(all_students) == 3
            
            emails = [s.email for s in all_students]
            assert 'john.doe@example.com' in emails
            assert 'jane.smith@example.com' in emails
            assert 'bob.johnson@example.com' in emails


class TestEdgeCases:
    """Test cases for edge cases and error scenarios"""
    
    def test_create_student_with_none_json(self, client):
        """Test creating a student when no JSON is provided"""
        response = client.post(f'{URL_PREFIX}/students',
                              data=None,
                              content_type='application/json')
        
        assert response.status_code == 400

    @pytest.mark.parametrize("invalid_age", [-1, 0, 150, "twenty", None])
    def test_create_student_invalid_age(self, client, sample_student_data, invalid_age):
        """Test creating a student with invalid age values"""
        invalid_data = sample_student_data.copy()
        invalid_data['age'] = invalid_age
        
        response = client.post(f'{URL_PREFIX}/students',
                              data=json.dumps(invalid_data),
                              content_type='application/json')
        
        # The API should handle this gracefully
        # The exact status code depends on your validation logic
        assert response.status_code in [400, 500]

    def test_update_student_with_empty_json(self, client, created_student):
        """Test updating a student with empty JSON"""
        student_id = created_student['id']
        
        response = client.put(f'/api/v1/students/{student_id}',
                             data=json.dumps({}),
                             content_type='application/json')
        
        # Should succeed but not change anything
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == created_student['first_name']
        assert data['last_name'] == created_student['last_name']
        assert data['age'] == created_student['age']
        assert data['email'] == created_student['email']
