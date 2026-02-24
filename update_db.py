from app.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
db.execute(text("UPDATE subjects SET id='CS108' WHERE name='Adv. Python'"))
db.execute(text("UPDATE subjects SET section='I' WHERE section='i'"))
db.commit()
print('updated')
