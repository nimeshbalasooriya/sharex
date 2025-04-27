from flask import Flask, request, session, redirect, url_for, render_template, send_from_directory
from models import db, User, FileShare
import os

app = Flask(__name__)
app.secret_key = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        session['user_id'] = user.id
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        receiver_code = request.form['receiver_code']
        receiver = User.query.filter_by(unique_code=receiver_code).first()
        if receiver:
            session['receiver_id'] = receiver.id
            return redirect('/send-file')
        else:
            return "User Not Found"
    return render_template('dashboard.html', user=user)

@app.route('/send-file', methods=['GET', 'POST'])
def send_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        sender_id = session['user_id']
        receiver_id = session['receiver_id']

        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        shared = FileShare(sender_id=sender_id, receiver_id=receiver_id, filename=filename, filepath=save_path)
        db.session.add(shared)
        db.session.commit()
        return "File Shared Successfully! <a href='/dashboard'>Go back</a>"

    return '''
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Send">
        </form>
    '''

@app.route('/my-files')
def my_files():
    user_id = session['user_id']
    files = FileShare.query.filter_by(receiver_id=user_id).all()
    return render_template('my_files.html', files=files)

@app.route('/download/<int:file_id>')
def download(file_id):
    file = FileShare.query.get(file_id)
    return send_from_directory(directory=os.path.dirname(file.filepath), path=os.path.basename(file.filepath), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
