from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Post
from forms import LoginForm, PostForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db.init_app(app)

# Сначала создаем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Указываем имя функции представления для логина
login_manager.login_view = 'login'  # Исправлено: имя функции, а не URL

# Загрузчик пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Регистрация маршрутов
@app.route('/')
def home():
    if current_user.is_authenticated:
        posts = Post.query.all()
    else:
        posts = Post.query.filter_by(is_private=False).all()
    return render_template('home.html', posts=posts)

# ОБРАТИТЕ ВНИМАНИЕ: имя функции 'login' должно совпадать с login_manager.login_view
@app.route('/login', methods=['GET', 'POST'])
def login():  # Имя функции используется в url_for()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            is_private=form.is_private.data,
            author_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Пост успешно создан!')
        return redirect(url_for('home'))
    return render_template('post.html', form=form)


@app.route('/db')
def show_db():
    users = User.query.all()
    posts = Post.query.all()

    output = "<h1>Database Contents</h1>"

    output += "<h2>Users</h2><ul>"
    for user in users:
        output += f"<li>{user.id}: {user.username}</li>"
    output += "</ul>"

    output += "<h2>Posts</h2><ul>"
    for post in posts:
        output += f"<li>{post.id}: {post.title} (Private: {post.is_private})</li>"
    output += "</ul>"

    return output

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Добавляем тестового пользователя
        if not User.query.filter_by(username='test').first():
            test_user = User(username='test', password='password')
            db.session.add(test_user)
            db.session.commit()
            print("Тестовый пользователь создан")
    app.run(debug=True)