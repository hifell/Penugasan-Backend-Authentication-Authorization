from connection import get_db, engine, Base
from user import User
from auth_util import hash_password

Base.metadata.create_all(bind=engine)
db = next(get_db())
admin = User(username='admin', hashed_password=hash_password('admin123'), role='admin')
db.add(admin)
db.commit()
print('Akun admin berhasil dibuat!')