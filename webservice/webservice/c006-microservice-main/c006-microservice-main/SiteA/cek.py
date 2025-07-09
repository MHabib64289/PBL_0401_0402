from peewee import *
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'cars.db')
db = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = db

class TBCarsWeb(BaseModel):
    carname = TextField()
    carbrand = TextField()
    carmodel = TextField()
    carprice = TextField()
    description = TextField(null=True)

db.connect()
for car in TBCarsWeb.select():
    print(car.carname, car.carbrand, car.carmodel)
