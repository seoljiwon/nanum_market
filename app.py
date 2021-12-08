from flask import Flask, render_template, redirect, request, session
from flask.helpers import url_for
import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv(verbose=True)

app = Flask(__name__)
# 세션에서 사용될 SECRET_KEY 설정
SECRET_KEY = os.getenv('SECRET_KEY')
app.secret_key = SECRET_KEY

# postgres DB 연결
DB_CONFIG = os.getenv('DB_CONFIG')
connect = psycopg2.connect(DB_CONFIG)
cur = connect.cursor()

# 테이블 생성
# cur.execute('DROP TABLE user_like;')
# cur.execute('DROP TABLE post_like;')
# cur.execute('DROP TABLE comment;')
# cur.execute('DROP TABLE buy;')
# cur.execute('DROP TABLE post;')
# cur.execute('DROP TABLE users;')

# cur.execute('CREATE TABLE users (id varchar(20), password varchar(20), phone numeric(11, 0), phone_public boolean, primary key(id));')
# cur.execute('CREATE TABLE post (id SERIAL, user_id varchar(20), title varchar(20) not null, content text, location text, image text, created_at timestamp default now(), updated_at timestamp default now(), is_closed boolean, primary key(id), foreign key (user_id) references users on delete cascade);')
# cur.execute('CREATE TABLE comment (id SERIAL, user_id varchar(20), post_id SERIAL, content text, created_at timestamp default now(), primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
# cur.execute('CREATE TABLE buy (id SERIAL, user_id varchar(20), post_id SERIAL, created_at timestamp default now(), state varchar(10) check (state in (\'is_posted\', \'is_waiting\', \'is_done\')), sending_method varchar(10) check (sending_method in (\'delivery\', \'receipt\')),primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
# cur.execute('CREATE TABLE post_like (id SERIAL, user_id varchar(20), post_id SERIAL, primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
# cur.execute('CREATE TABLE user_like (id SERIAL, user_id varchar(20), nice_user_id varchar(20), primary key(id), foreign key (user_id) references users on delete cascade, foreign key (nice_user_id) references users on delete cascade);')
# connect.commit()


# 메인 랜딩 페이지
@app.route('/')
def landing():
    if 'id' in session:
        session_id = session['id']
        return render_template('landing.html', session_id = session_id)
    
    return render_template('landing.html')

# users: 로그인 기능
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['id'] = request.form['id']
        return redirect(url_for('landing'))

    return render_template('users/login.html')
    
# users: 로그아웃 기능
@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('landing'))

# users: 회원가입 기능
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        cur.execute('INSERT INTO users VALUES(\'{}\', \'{}\');'.format(id, password))
        connect.commit()
        return redirect(url_for('login'))

    return render_template('users/signup.html')

# post: 게시글 작성 기능
@app.route('/post/create', methods=['GET', 'POST'])
def post_create():
    if request.method == 'POST':
        if 'id' in session:
            user_id = session['id']
            title = request.form['title']
            content = request.form['content']
            location = request.form['location']
            image = request.files['image']
            image.save('static/uploads/' + secure_filename(image.filename))

            is_closed = False
            cur.execute('INSERT INTO post (user_id, title, content, location, image, is_closed) VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\') RETURNING id;'.format(user_id, title, content, location, 'uploads/'+secure_filename(image.filename), is_closed))
            connect.commit()

            post_id = cur.fetchall()
            return redirect(url_for('post_detail', id = post_id[0]))

    return render_template('post/post_create.html')

# post: 특정 게시글 보기 기능
@app.route('/post/<id>', methods=['GET'])
def post_detail(id):
    cur.execute('SELECT * FROM post WHERE id = \'{}\';'.format(id))
    post = cur.fetchall()

    return render_template('post/post_detail.html', post = post[0])


if __name__ == '__main__':
    app.run()

