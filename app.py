from flask import Flask,render_template,request,redirect,url_for,session,flash
from model import*
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

current_dir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(current_dir,"database.sqlite3")
app.secret_key="your_secretkey"
db.init_app(app)
app.app_context().push()


def auth_req(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

def admin_req(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user_id' not in session or session['user_type'] != 'admin':
            flash('You need admin privileges to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return redirect(url_for('login'))
            
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_type'] = user.user_type
            if user.user_type == 'admin':
                    return redirect(url_for('admin'))
            else:
                    return redirect(url_for('student'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        level = request.form['level']
        dob = request.form['dob']
        phone_no = request.form['phone_no']

        if Users.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        user = Users(
            name=name,
            email=email,
            password=generate_password_hash(password),
            level=level,
            dob=dob,
            phone_no=phone_no,
            user_type='student'
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html')

def create_default_admin():
    try:
        admin = Users.query.filter_by(email='admin@gmail.com').first()
        if not admin:
            admin = Users(
                name='Admin',
                email='admin@gmail.com',
                password=generate_password_hash('admin123'),
                user_type='admin',
            )
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        # If there's an error (like duplicate email), try to update existing admin
        admin = Users.query.filter_by(email='admin@gmail.com').first()
        if admin:
            admin.user_type = 'admin'
            admin.level = 'admin'
            admin.password = generate_password_hash('admin123')  # Update password with hash
            db.session.commit()

#Admin

@app.route('/admin/')
@admin_req
def admin():
    subjects = Subject.query.all()
    return render_template('admin_dashboard.html', subjects=subjects)

#subject
@app.route('/admin/subject/add/', methods=['GET', 'POST'])
@admin_req
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        level = request.form.get('level') 
        additional_details = request.form.get('additional_details', '')
        subject = Subject(name=name, description=description, level=level,additional_details=additional_details)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully', 'success')
        return redirect(url_for('admin'))
    return render_template('Subject/add_subject.html')

@app.route('/admin/subject/<int:subject_id>/edit/', methods=['GET', 'POST'])
@admin_req
def edit_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form.get('description')
        db.session.commit()
        flash('Subject updated successfully', 'success')
        return redirect(url_for('admin'))
    return render_template('Subject/edit_subject.html', subject=subject)
        
@app.route('/admin/subject/<int:subject_id>/delete/')
@admin_req
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('Subject/delete_subject.html', subject=subject)

@app.route('/admin/subject/<int:subject_id>/delete/', methods=['POST'])
@admin_req
def delete_subject_post(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/subject/<int:subject_id>/')
@auth_req
def show_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject not found', 'danger')
        return redirect(url_for('admin'))
    
    # Check if user is admin or if subject matches student's level
    if session['user_type'] == 'student':
        user = Users.query.get(session['user_id'])
        if subject.level != user.level:
            flash('You can only view subjects for your level', 'warning')
            return redirect(url_for('student'))
    
    return render_template('Subject/show_subject.html', subject=subject)

#chapter
@app.route('/admin/subject/<int:subject_id>/chapter/add/', methods=['GET', 'POST'])
@admin_req
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully', 'success')
        return redirect(url_for('show_subject', subject_id=subject_id))
    return render_template('Chapter/add.html', subject=subject)

@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/edit/', methods=['GET', 'POST'])
@admin_req
def edit_chapter(subject_id, chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('show_subject', subject_id=subject_id))
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form.get('description', '')
        db.session.commit()
        flash('Chapter updated successfully', 'success')
        return redirect(url_for('show_subject', subject_id=subject_id))
    return render_template('Chapter/edit.html', chapter=chapter, subject_id=subject_id)

@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/delete/')
@admin_req
def delete_chapter(subject_id, chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('show_subject', subject_id=subject_id))
    return render_template('Chapter/delete.html', chapter=chapter, subject_id=subject_id)

@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/delete/', methods=['POST'])
@admin_req
def delete_chapter_post(subject_id, chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('show_subject', subject_id=subject_id))
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('show_subject', subject_id=subject_id))

@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/')
@admin_req
def show_chapter(subject_id, chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('show_subject', subject_id=subject_id))
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('Chapter/show.html', chapter=chapter, subject_id=subject_id, quizzes=quizzes)

#quiz
@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/add/', methods=['GET', 'POST'])
@admin_req
def add_quiz(subject_id, chapter_id):
    chapter = Chapter.query.get(chapter_id)
    subjects = Subject.query.all()
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('show_subject', subject_id=subject_id))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        duration = int(request.form.get('duration', 30))
        pass_percentage = int(request.form.get('pass_percentage', 60))
        total_questions=int(request.form.get('total_questions'))
        quiz = Quiz(name=name, description=description, duration=duration, pass_percentage=pass_percentage, chapter_id=chapter_id,subject_id=subject_id,  # Add this
            total_questions=total_questions)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully', 'success')
        return redirect(url_for('show_chapter', subject_id=subject_id, chapter_id=chapter_id))
    return render_template('Quiz/add.html', chapter=chapter, subject_id=subject_id, subjects=subjects)


@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/edit/', methods=['GET', 'POST'])
@admin_req
def edit_quiz(subject_id, chapter_id, quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('show_chapter', subject_id=subject_id, chapter_id=chapter_id))
    if request.method == 'POST':
        quiz.name = request.form['name']
        quiz.description = request.form.get('description', '')
        quiz.duration = int(request.form.get('duration', 30))
        quiz.pass_percentage = int(request.form.get('pass_percentage', 60))
        db.session.commit()
        flash('Quiz updated successfully', 'success')
        return redirect(url_for('show_chapter', subject_id=subject_id, chapter_id=chapter_id))
    return render_template('Quiz/edit.html', quiz=quiz)

@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/delete/')
@admin_req
def delete_quiz(subject_id, chapter_id, quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('show_chapter', subject_id=subject_id, chapter_id=chapter_id))
    return render_template('Quiz/delete_quiz.html', quiz=quiz)

@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/delete/', methods=['POST'])
@admin_req
def delete_quiz_post(subject_id, chapter_id, quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('show_chapter', subject_id=subject_id, chapter_id=chapter_id))
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully', 'success')
    return redirect(url_for('show_chapter', subject_id=subject_id, chapter_id=chapter_id))

@app.route('/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/')
@admin_req
def show_quiz(subject_id, chapter_id, quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('show_chapter', subject_id=subject_id, chapter_id=chapter_id))
    return render_template('Quiz/show_quiz.html', quiz=quiz)

#question
@app.route('/quiz/<int:quiz_id>/add_question/', methods=['GET', 'POST'])
@admin_req
def add_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash("Quiz does not exist", 'danger')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']
        explanation = request.form.get('explanation', '')
        score = int(request.form.get('score', 1))  # Default to 1 if not provided

        # Convert letter option to number
        option_map = {'A': '1', 'B': '2', 'C': '3', 'D': '4'}
        correct_option_number = option_map.get(correct_option, correct_option)

        question = Questions(
            quiz_id=quiz_id,
            question_statement=question_text,
            option_1=option_a,
            option_2=option_b,
            option_3=option_c,
            option_4=option_d,
            correct_option=correct_option_number,
            Additional_field=explanation,
            score=score
        )
        db.session.add(question)
        db.session.commit()
        flash("Question added successfully", 'success')
        return redirect(url_for('show_quiz', subject_id=quiz.subject_id, chapter_id=quiz.chapter_id, quiz_id=quiz_id))
    return render_template("Questions/add_question.html", quiz=quiz)

@app.route('/question/<int:id>/edit/', methods=['GET', 'POST'])
@admin_req
def edit_question(id):
    question = Questions.query.get(id)
    if not question:
        flash("Question does not exist", 'danger')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        question.question_statement = request.form['question_text']
        question.option_1 = request.form['option_a']
        question.option_2 = request.form['option_b']
        question.option_3 = request.form['option_c']
        question.option_4 = request.form['option_d']
        question.correct_option = request.form['correct_option']
        question.Additional_field = request.form.get('explanation', '')
        question.score = int(request.form.get('score', 1))  # Default to 1 if not provided

        db.session.commit()
        flash("Question updated successfully", 'success')
        return redirect(url_for('show_quiz', subject_id=question.quiz.subject_id, chapter_id=question.quiz.chapter_id, quiz_id=question.quiz_id))

    return render_template("Questions/edit_question.html", question=question)

@app.route('/question/<int:id>/delete/')
@admin_req
def delete_question(id):
    question = Questions.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('admin'))
    quiz = Quiz.query.get(question.quiz_id)
    return render_template("Questions/delete_question.html", question=question, quiz=quiz)

@app.route('/question/<int:id>/delete/', methods=['POST'])
@admin_req
def delete_question_post(id):
    question = Questions.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('admin'))
    
    # Get quiz information before deleting the question
    subject_id = question.quiz.subject_id
    chapter_id = question.quiz.chapter_id
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully', 'success')
    return redirect(url_for('show_quiz', subject_id=subject_id, chapter_id=chapter_id, quiz_id=quiz_id))

@app.route('/student/')
@auth_req 
def student():
    if 'user_name' in session and session['user_type']=='student':
        user = Users.query.get(session['user_id'])
        # Get all quizzes
        all_quizzes = Quiz.query.all()
        
        # Get completed quizzes with scores and status
        completed_quizzes = []
        for quiz in user.quizzes:
            association = db.session.query(user_quiz_association).filter_by(
                user_id=user.id,
                quiz_id=quiz.id
            ).first()
            if association:
                quiz.score = association.score
                quiz.status = association.status
                completed_quizzes.append(quiz)
        
        # Get available quizzes (not completed)
        available_quizzes = [quiz for quiz in all_quizzes if quiz not in completed_quizzes]
        
        # Get subjects matching student's level
        level_subjects = Subject.query.filter_by(level=user.level).all()
        
        return render_template("student_dashboard.html",
                             name=session['user_name'],
                             available_quizzes=available_quizzes,
                             completed_quizzes=completed_quizzes,
                             level_subjects=level_subjects)
    return redirect(url_for('login'))

@app.route('/edit_profile/',methods=['GET','POST'])
def edit_profile():
    if 'user_id' not in session or session['user_type']!='student':
        flash('You need to login first', 'danger')
        return redirect(url_for('login'))
    
    user = Users.query.get(session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('login'))

    if request.method=='POST':
        user.name = request.form['name']
        user.email = request.form['student_mail'].strip()
        user.dob = request.form['dob']
        user.phone_no = request.form['phone_no']
        user.level = request.form['level']

        new_password = request.form['password']
        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
            
        session['user_name'] = user.name
            
        return redirect(url_for('student'))
    return render_template('edit_profile.html', user=user)

@app.route('/logout/')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin/search/')
@admin_req
def admin_search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')
    
    subjects = []
    chapters = []
    users = []
    
    if query:
        if search_type in ['all', 'subjects']:
            subjects = Subject.query.filter(
                (Subject.name.ilike(f'%{query}%')) |
                (Subject.description.ilike(f'%{query}%'))
            ).all()
            
        if search_type in ['all', 'chapters']:
            chapters = Chapter.query.filter(
                (Chapter.name.ilike(f'%{query}%')) |
                (Chapter.description.ilike(f'%{query}%'))
            ).all()
            
        if search_type in ['all', 'users']:
            users = Users.query.filter(
                (Users.name.ilike(f'%{query}%')) |
                (Users.email.ilike(f'%{query}%'))
            ).all()
    
    return render_template('admin_search.html', 
                         query=query, 
                         search_type=search_type,
                         subjects=subjects,
                         chapters=chapters,
                         users=users)

@app.route('/student/search/')
@auth_req
def student_search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')
    
    subjects = []
    chapters = []
    
    if query:
        if search_type in ['all', 'subjects']:
            subjects = Subject.query.filter(
                (Subject.name.ilike(f'%{query}%')) |
                (Subject.description.ilike(f'%{query}%'))
            ).all()
            
        if search_type in ['all', 'chapters']:
            chapters = Chapter.query.filter(
                (Chapter.name.ilike(f'%{query}%')) |
                (Chapter.description.ilike(f'%{query}%'))
            ).all()
    
    return render_template('student_search.html', 
                         query=query, 
                         search_type=search_type,
                         subjects=subjects,
                         chapters=chapters)

@app.route('/student/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/take/', methods=['GET'])
@auth_req
def take_quiz(subject_id, chapter_id, quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist', 'danger')
        return redirect(url_for('student'))
    
    # Check if user has already taken this quiz
    user = Users.query.get(session['user_id'])
    if quiz in user.quizzes:
        flash('You have already taken this quiz', 'warning')
        return redirect(url_for('student'))
    
    return render_template('Quiz/take_quiz.html', quiz=quiz)

@app.route('/student/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>/submit/', methods=['POST'])
@auth_req
def submit_quiz(subject_id, chapter_id, quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist', 'danger')
        return redirect(url_for('student'))
    
    user = Users.query.get(session['user_id'])
    if quiz in user.quizzes:
        flash('You have already taken this quiz', 'warning')
        return redirect(url_for('student'))
    
    # Calculate score
    total_score = 0
    max_score = sum(question.score for question in quiz.questions)
    
    for question in quiz.questions:
        answer = request.form.get(f'question_{question.id}')
        # Convert answer to string for comparison since correct_option is stored as string
        if answer and str(answer) == question.correct_option:
            total_score += question.score
    
    # Calculate percentage
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    
    # Determine status
    status = "Passed" if percentage >= quiz.pass_percentage else "Failed"
    
    # Create the association with score, status, and current date
    db.session.execute(
        user_quiz_association.insert().values(
            user_id=user.id,
            quiz_id=quiz.id,
            score=percentage,
            status=status,
            date=datetime.utcnow()
        )
    )
    
    db.session.commit()
    
    flash(f'Quiz submitted! Your score: {percentage:.1f}% ({status})', 'success')
    return redirect(url_for('student'))

@app.route('/student/summary/')
@auth_req
def student_summary():
    if session['user_type'] != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('admin'))
    
    user = Users.query.get(session['user_id'])
    
    # Get all completed quizzes with scores
    completed_quizzes = []
    total_score = 0
    total_quizzes = 0
    passed_quizzes = 0
    failed_quizzes = 0
    
    for quiz in user.quizzes:
        association = db.session.query(user_quiz_association).filter_by(
            user_id=user.id,
            quiz_id=quiz.id
        ).first()
        if association:
            quiz.score = association.score
            quiz.status = association.status
            quiz.date = association.date
            completed_quizzes.append(quiz)
            total_score += quiz.score
            total_quizzes += 1
            if quiz.status == 'Passed':
                passed_quizzes += 1
            else:
                failed_quizzes += 1
    
    # Calculate average score
    average_score = (total_score / total_quizzes) if total_quizzes > 0 else 0
    
    # Get subject performance
    subject_performance = {}
    for quiz in completed_quizzes:
        subject = quiz.chapter.subject
        if subject.name not in subject_performance:
            subject_performance[subject.name] = {'total_score': 0, 'count': 0}
        subject_performance[subject.name]['total_score'] += quiz.score
        subject_performance[subject.name]['count'] += 1
    
    # Calculate average scores for each subject
    for subject in subject_performance:
        subject_performance[subject]['average_score'] = (
            subject_performance[subject]['total_score'] / 
            subject_performance[subject]['count']
        )
    
    # Find best and worst subjects
    best_subject = {'name': 'N/A', 'average_score': 0}
    worst_subject = {'name': 'N/A', 'average_score': 100}
    
    for subject_name, data in subject_performance.items():
        if data['average_score'] > best_subject['average_score']:
            best_subject = {'name': subject_name, 'average_score': data['average_score']}
        if data['average_score'] < worst_subject['average_score']:
            worst_subject = {'name': subject_name, 'average_score': data['average_score']}
    
    # Sort completed quizzes by date (most recent first)
    completed_quizzes.sort(key=lambda x: x.date, reverse=True)
    recent_quizzes = completed_quizzes[:5]  # Get 5 most recent quizzes
    
    return render_template('student_summary.html',
                         total_quizzes=total_quizzes,
                         passed_quizzes=passed_quizzes,
                         failed_quizzes=failed_quizzes,
                         average_score=average_score,
                         best_subject=best_subject,
                         worst_subject=worst_subject,
                         recent_quizzes=recent_quizzes)

@app.route('/admin/summary/')
@admin_req
def admin_summary():
    # Get basic statistics
    total_students = Users.query.filter_by(user_type='student').count()
    total_subjects = Subject.query.count()
    total_quizzes = Quiz.query.count()
    active_students = Users.query.filter_by(user_type='student').count()  # You might want to add an 'active' field to Users model
    
    # Get all students with their performance
    students = Users.query.filter_by(user_type='student').all()
    for student in students:
        # Calculate student's quiz statistics
        completed_quizzes = []
        total_score = 0
        
        for quiz in student.quizzes:
            association = db.session.query(user_quiz_association).filter_by(
                user_id=student.id,
                quiz_id=quiz.id
            ).first()
            if association:
                quiz.score = association.score
                completed_quizzes.append(quiz)
                total_score += quiz.score
        
        student.quizzes_taken = len(completed_quizzes)
        student.average_score = (total_score / student.quizzes_taken) if student.quizzes_taken > 0 else 0
    
    # Get subject performance data
    subjects = Subject.query.all()
    subject_names = []
    subject_scores = []
    
    for subject in subjects:
        subject_total_score = 0
        subject_quiz_count = 0
        
        for chapter in subject.chapters:
            for quiz in chapter.quizzes:
                associations = db.session.query(user_quiz_association).filter_by(quiz_id=quiz.id).all()
                for association in associations:
                    subject_total_score += association.score
                    subject_quiz_count += 1
        
        if subject_quiz_count > 0:
            subject_names.append(subject.name)
            subject_scores.append(subject_total_score / subject_quiz_count)
    
    # Get level distribution
    level_counts = {}
    level_labels = []
    for student in students:
        if student.level not in level_counts:
            level_counts[student.level] = 0
            level_labels.append(student.level)
        level_counts[student.level] += 1
    
    return render_template('admin_summary.html',
                         total_students=total_students,
                         total_subjects=total_subjects,
                         total_quizzes=total_quizzes,
                         active_students=active_students,
                         students=students,
                         subject_names=subject_names,
                         subject_scores=subject_scores,
                         level_labels=level_labels,
                         level_counts=list(level_counts.values()))

@app.route('/admin/student/<int:student_id>/')
@admin_req
def view_student_details(student_id):
    student = Users.query.get_or_404(student_id)
    if student.user_type != 'student':
        flash('Invalid student ID', 'danger')
        return redirect(url_for('admin_summary'))
    
    # Get student's quiz history
    completed_quizzes = []
    for quiz in student.quizzes:
        association = db.session.query(user_quiz_association).filter_by(
            user_id=student.id,
            quiz_id=quiz.id
        ).first()
        if association:
            quiz.score = association.score
            quiz.status = association.status
            quiz.date = association.date
            completed_quizzes.append(quiz)
    
    # Sort by date
    completed_quizzes.sort(key=lambda x: x.date, reverse=True)
    
    return render_template('admin_student_details.html',
                         student=student,
                         completed_quizzes=completed_quizzes)

if __name__=='__main__':
    #db.drop_all()
    with app.app_context():
        #db.drop_all()  # Drop all tables first
        db.create_all()  # Create all tables with new schema
        create_default_admin()  # Then create admin user
    app.run(debug=True)
