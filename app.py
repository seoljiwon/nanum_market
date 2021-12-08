from flask import Flask, render_template
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

DB_CONFIG = os.getenv('DB_CONFIG')

app = Flask(__name__)

connect = psycopg2.connect(DB_CONFIG)
cur = connect.cursor()

# 테이블 생성
cur.execute('DROP TABLE user_like;')
cur.execute('DROP TABLE post_like;')
cur.execute('DROP TABLE comment;')
cur.execute('DROP TABLE buy;')
cur.execute('DROP TABLE post;')
cur.execute('DROP TABLE users;')

cur.execute('CREATE TABLE users (id varchar(20), password varchar(20), phone numeric(11, 0), phone_public boolean, primary key(id));')
cur.execute('CREATE TABLE post (id SERIAL, user_id varchar(20), title varchar(20) not null, content text, location text, image_urls text, created_at timestamp default now(), updated_at timestamp default now(), is_closed boolean, primary key(id), foreign key (user_id) references users on delete cascade);')
cur.execute('CREATE TABLE comment (id SERIAL, user_id varchar(20), post_id SERIAL, content text, created_at timestamp default now(), primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
cur.execute('CREATE TABLE buy (id SERIAL, user_id varchar(20), post_id SERIAL, created_at timestamp default now(), state varchar(10) check (state in (\'is_posted\', \'is_waiting\', \'is_done\')), sending_method varchar(10) check (sending_method in (\'delivery\', \'receipt\')),primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
cur.execute('CREATE TABLE post_like (id SERIAL, user_id varchar(20), post_id SERIAL, primary key(id), foreign key (user_id) references users on delete cascade, foreign key (post_id) references post on delete cascade);')
cur.execute('CREATE TABLE user_like (id SERIAL, user_id varchar(20), nice_user_id varchar(20), primary key(id), foreign key (user_id) references users on delete cascade, foreign key (nice_user_id) references users on delete cascade);')
connect.commit()


@app.route('/')
def landing():
    return render_template('landing.html')


if __name__ == '__main__':
    app.run()

