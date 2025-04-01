from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from werkzeug.security import generate_password_hash

db=SQLAlchemy()

user_quiz_association = db.Table(
    'user_quiz',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('quiz_id', db.Integer, db.ForeignKey('quiz.id'), primary_key=True),
    db.Column('enrollment_date', db.DateTime, default=datetime.utcnow),  # Tracks when user enrolled
    db.Column('score', db.Float, nullable=True),  # Store the percentage score
    db.Column('status', db.String(20), nullable=True),  # Could be "Passed", "Failed", "Not Attempted"
    db.Column('date', db.DateTime, default=datetime.utcnow)  # Date when quiz was taken
)

class Users(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True) 
    name=db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password=db.Column(db.String)
    level=db.Column(db.String)
    dob=db.Column(db.String)
    user_type=db.Column(db.String)
    phone_no=db.Column(db.String)

    quizzes = db.relationship('Quiz', secondary=user_quiz_association, back_populates="users")


class Subject(db.Model):
    __tablename__='subject'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    level = db.Column(db.String, nullable=False)
    description=db.Column(db.String)
    additional_details=db.Column(db.String)

class Chapter(db.Model):
    __tablename__='chapter'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False) 
    name = db.Column(db.String, unique=True, nullable=False)
    description=db.Column(db.String)
    additional_details=db.Column(db.String)

    subject = db.relationship('Subject', backref=db.backref('chapters', cascade="all, delete-orphan"))
    quizzes = db.relationship('Quiz', backref='chapter', cascade="all, delete-orphan")



class Quiz(db.Model):
    __tablename__='quiz'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)  # Make sure this exists
    duration = db.Column(db.Integer, nullable=False)
    pass_percentage = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)


    users = db.relationship('Users', secondary=user_quiz_association, back_populates="quizzes")
    subject = db.relationship('Subject', foreign_keys=[subject_id], backref=db.backref('quizzes', lazy=True))


class Questions(db.Model):
    __tablename__='questions'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    quiz_id=db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    question_statement=db.Column(db.String(500),nullable=False)
    option_1=db.Column(db.String(200),nullable=False)
    option_2=db.Column(db.String(200),nullable=False)
    option_3=db.Column(db.String(200),nullable=False)
    option_4=db.Column(db.String(200),nullable=False)
    correct_option=db.Column(db.String(1),nullable=False)
    Additional_field=db.Column(db.String(500))
    score = db.Column(db.Integer, nullable=False, default=1)  # Default score is 1 point
    
    quiz = db.relationship('Quiz', backref=db.backref('questions', cascade="all, delete-orphan"))


class Scores(db.Model):
    __tablename__='scores'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    quiz_id=db.Column(db.Integer,db.ForeignKey('quiz.id'))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    time_stamp_of_attempt=db.Column(db.DateTime,default=datetime.utcnow, nullable=False)
    total_score=db.Column(db.Integer,nullable=False)
    Additional_field=db.Column(db.String)
    
    user=db.relationship('Users',backref='scores')
    quiz=db.relationship('Quiz',backref='scores')

admin = Users(
    name='Admin',
    email='admin@gmail.com',
    password=generate_password_hash('admin123'),  # Default password
    level='admin',
    dob='1990-01-01',
    phone_no='0000000000',
    user_type='admin'
)

