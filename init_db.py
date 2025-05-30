from app import app, db
from models import User, Post

with app.app_context():
    db.create_all()
    print("Таблицы созданы")

    # Создаем тестового пользователя
    if not User.query.filter_by(username='test').first():
        user = User(username='test', password='password')
        db.session.add(user)
        db.session.commit()
        print("Тестовый пользователь создан")