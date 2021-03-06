from flask import Flask, render_template, redirect, jsonify, request, session
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
# cur.execute('CREATE TABLE buy (id SERIAL, user_id varchar(20), post_id SERIAL, created_at timestamp default now(), status varchar(10) check (status in (\'is_posted\', \'is_waiting\', \'is_done\')), sending_method varchar(10) check (sending_method in (\'delivery\', \'receipt\')),primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
# cur.execute('CREATE TABLE post_like (id SERIAL, user_id varchar(20), post_id SERIAL, primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
# cur.execute('CREATE TABLE user_like (id SERIAL, user_id varchar(20), nice_user_id varchar(20), primary key(id), foreign key (user_id) references users on delete cascade, foreign key (nice_user_id) references users on delete cascade);')
# connect.commit()


# 메인 랜딩 페이지
@app.route('/')
def landing():
    if 'id' in session:
        session_id = session['id']
        cur.execute('SELECT count(*) FROM post, buy WHERE post.id = buy.post_id and buy.user_id = \'{}\' and buy.status=\'is_waiting\';'.format(session_id))
        buy_waiting_count = cur.fetchall()
        cur.execute('SELECT count(*) FROM post natural join post_like WHERE post_like.user_id = \'{}\';'.format(session_id))
        post_like_count = cur.fetchall()

        return render_template('landing.html', session_id = session_id, buy_waiting_count = buy_waiting_count[0][0], post_like_count = post_like_count[0][0])
    
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
        phone = request.form['phone']
        phone_public = request.form['phone_public'] 
        cur.execute('INSERT INTO users VALUES(\'{}\', \'{}\', \'{}\', \'{}\');'.format(id, password, phone, phone_public))
        connect.commit()
        return redirect(url_for('login'))

    return render_template('users/signup.html')

# user_like: 유저 좋아요 기능
@app.route('/user/<id>/like', methods=['POST'])
def user_like(id):
    if request.method == 'POST':
        if 'id' in session:
            user_id = session['id']

            cur.execute('SELECT * FROM user_like WHERE nice_user_id = \'{}\' and user_id = \'{}\';'.format(id, user_id))
            is_liked = (len(cur.fetchall()) != 0)

            if is_liked:
                cur.execute('DELETE FROM user_like WHERE nice_user_id = \'{}\' and user_id = \'{}\';'.format(id, user_id))
                connect.commit()
                
            else:
                cur.execute('INSERT INTO user_like (nice_user_id, user_id) VALUES (\'{}\', \'{}\');'.format(id, user_id))
                connect.commit()
                
            is_liked = not is_liked
            login_required = False
            return jsonify(nice_user_id = id, is_liked = is_liked, login_required = login_required)
        else:
            login_required = True
            return jsonify(login_required = login_required)

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
    if 'id' in session:
        user_id = session['id']

    cur.execute('SELECT * FROM post WHERE id = \'{}\';'.format(id))
    post = cur.fetchall()

    # 좋아요 정보
    cur.execute('SELECT count(user_id) FROM post_like GROUP BY post_id HAVING post_id = \'{}\';'.format(id))
    like_count = cur.fetchall()
    if not like_count:
        like_count = [[0 for col in range(1)] for row in range(1)]
        like_count[0][0] = 0

    print(like_count)
    
    cur.execute('SELECT * FROM post_like WHERE post_id = \'{}\' and user_id = \'{}\';'.format(id, user_id))
    is_liked = (len(cur.fetchall()) != 0)

    # 댓글 정보
    cur.execute('SELECT * FROM comment WHERE post_id = \'{}\' and user_id = \'{}\';'.format(id, user_id))
    comments = cur.fetchall()
    return render_template('post/post_detail.html', post = post[0], like_count = like_count[0][0], is_liked = is_liked, comments = comments)

# post: 게시글 수정 기능
@app.route('/post/<id>/update', methods=['GET', 'POST'])
def post_update(id):
    if request.method == 'POST':
        if 'id' in session:
            title = request.form['title']
            content = request.form['content']
            location = request.form['location']
            image = request.files['image']
            image.save('static/uploads/' + secure_filename(image.filename))

            is_closed = request.form['is_closed']
            
            cur.execute('UPDATE post SET title = \'{}\', content = \'{}\', location = \'{}\', image = \'{}\', is_closed = \'{}\', updated_at = now() WHERE id = \'{}\' RETURNING id;'.format(title, content, location, 'uploads/'+secure_filename(image.filename), is_closed, id))
            connect.commit()

            post_id = cur.fetchall()
            return redirect(url_for('post_detail', id = post_id[0]))

    cur.execute('SELECT * FROM post WHERE id = \'{}\';'.format(id))
    post = cur.fetchall()
    return render_template('post/post_update.html', post = post[0])

# post: 게시글 삭제 기능
@app.route('/post/<id>/delete', methods=['POST'])
def post_delete(id):
    if 'id' in session:
        cur.execute('DELETE FROM post WHERE id = \'{}\';'.format(id))
        connect.commit()
        return redirect(url_for('landing'))

# post: 전체 게시글 보기 기능
@app.route('/post/list', methods=['GET'])
def post_list():
    cur.execute('SELECT * FROM post;')
    posts = cur.fetchall()

    cur.execute('SELECT count(*) FROM post;')
    posts_count = cur.fetchall()

    return render_template('post/post_list.html', posts = posts, posts_count = posts_count[0][0])

# post_like: 게시글 좋아요 기능
@app.route('/post/<id>/like', methods=['POST'])
def post_like(id):
    if request.method == 'POST':
        if 'id' in session:
            user_id = session['id']

            cur.execute('SELECT * FROM post_like WHERE post_id = \'{}\' and user_id = \'{}\';'.format(id, user_id))
            is_liked = (len(cur.fetchall()) != 0)

            if is_liked:
                cur.execute('DELETE FROM post_like WHERE post_id = \'{}\' and user_id = \'{}\';'.format(id, user_id))
                connect.commit()
                
            else:
                cur.execute('INSERT INTO post_like (post_id, user_id) VALUES (\'{}\', \'{}\');'.format(id, user_id))
                connect.commit()
                
            is_liked = not is_liked
            login_required = False
            return jsonify(post_id = id, is_liked = is_liked, login_required = login_required)
        else:
            login_required = True
            return jsonify(login_required = login_required)

# comment: 게시글 댓글 기능
@app.route('/post/<id>/comment/create', methods=['POST'])
def post_comment_create(id):
    if request.method == 'POST':
        if 'id' in session:
            user_id = session['id']
            content = request.get_json()['content']

            cur.execute('INSERT INTO comment (post_id, user_id, content) VALUES (\'{}\', \'{}\', \'{}\') RETURNING id;'.format(id, user_id, content))
            connect.commit()

            comment_id = cur.fetchall()

            login_required = False 
            return jsonify(post_id = id, user_id = user_id, comment_id = comment_id, content = content, login_required = login_required)
        else:
            login_required = True
            return jsonify(login_required = login_required)

# buy: 나눔 받기 기능 - 나눔 방법 선택
@app.route('/post/<id>/buy', methods=['GET', 'POST'])
def post_buy(id):
    if request.method == 'POST':
        if 'id' in session:
            user_id = session['id']
            sending_method = request.form['sending_method']
            status = 'is_posted'

            cur.execute('INSERT INTO buy (post_id, user_id, status, sending_method) VALUES (\'{}\', \'{}\', \'{}\', \'{}\') RETURNING id;'.format(id, user_id, status, sending_method))
            connect.commit()

            buy_id = cur.fetchall()
            return redirect(url_for('post_buy_request', id = buy_id[0]))

    return render_template('post/post_buy.html', id = id)

# buy: 나눔 받기 기능 - 나눔 받기 요청
@app.route('/post/<id>/buy/request', methods=['GET', 'POST'])
def post_buy_request(id):
    if request.method == 'POST':
        if 'id' in session:
            user_id = session['id']
            status = request.form['status']
            
            cur.execute('UPDATE buy SET status = \'{}\' WHERE post_id = \'{}\' and user_id = \'{}\';'.format(status, id, user_id))
            connect.commit()

            return redirect(url_for('post_buy_request_waiting', id = id))

    return render_template('post/post_buy_request.html', id = id)

@app.route('/post/<id>/buy/request/waiting', methods=['GET'])
def post_buy_request_waiting(id):
    return render_template('post/post_but_request_waiting.html')

if __name__ == '__main__':
    app.run()

