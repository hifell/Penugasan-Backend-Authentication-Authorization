from connection import get_db
from user import User

db = next(get_db())
users = db.query(User).all()
for u in users:
    print(f"username: {u.username} | role: {u.role}")