from flask import Flask, jsonify
from peewee import *
from flask_restful import Resource, Api, reqparse
from playhouse.shortcuts import model_to_dict
import os

# Inisialisasi aplikasi Flask
app = Flask(__name__)
api = Api(app)

# === KONFIGURASI DATABASE ===
# Path ke database (1 folder di atas file ini)
db_path = os.path.join(os.path.dirname(__file__), '..', 'cars.db')
db = SqliteDatabase(db_path)

# === MODEL ===
class BaseModel(Model):
    class Meta:
        database = db

class TBCarsWeb(BaseModel):
    carname = TextField()
    carbrand = TextField()
    carmodel = TextField()
    carprice = TextField()
    description = TextField(null=True)

# === KELOLA KONEKSI DATABASE ===
@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()

@app.after_request
def _db_close(response):
    if not db.is_closed():
        db.close()
    return response

# === RESOURCE API ===
class CarResource(Resource):
    def get(self, car_id=None):
        if car_id:
            try:
                car = TBCarsWeb.get_by_id(car_id)
                return jsonify(model_to_dict(car))
            except TBCarsWeb.DoesNotExist:
                return {'message': f'Car with id {car_id} not found'}, 404
        else:
            cars = [model_to_dict(car) for car in TBCarsWeb.select()]
            return jsonify(cars)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('carname', required=True)
        parser.add_argument('carbrand', required=True)
        parser.add_argument('carmodel', required=True)
        parser.add_argument('carprice', required=True)
        args = parser.parse_args()

        # Debug: log data masuk dari form
        print("DATA DITERIMA DARI FORM:", args)

        new_car = TBCarsWeb.create(**args)
        return model_to_dict(new_car), 201

    def put(self, car_id):
        parser = reqparse.RequestParser()
        parser.add_argument('carname')
        parser.add_argument('carbrand')
        parser.add_argument('carmodel')
        parser.add_argument('carprice')
        args = parser.parse_args()
        update_data = {key: val for key, val in args.items() if val is not None}
        query = TBCarsWeb.update(update_data).where(TBCarsWeb.id == car_id)
        if query.execute() == 0:
            return {'message': f'Car with id {car_id} not found'}, 404
        updated_car = TBCarsWeb.get_by_id(car_id)
        return model_to_dict(updated_car), 200

    def delete(self, car_id):
        query = TBCarsWeb.delete().where(TBCarsWeb.id == car_id)
        if query.execute() == 0:
            return {'message': f'Car with id {car_id} not found'}, 404
        return {'message': f'Car with id {car_id} has been deleted'}, 200

class CarSearchResource(Resource):
    def get(self, keyword):
        cars = TBCarsWeb.select().where(
            (TBCarsWeb.carname.contains(keyword)) |
            (TBCarsWeb.carbrand.contains(keyword)) |
            (TBCarsWeb.carmodel.contains(keyword))
        )
        data = [model_to_dict(car) for car in cars]
        return jsonify(data)

# === ROUTING ===
api.add_resource(CarResource, '/cars', '/cars/', '/cars/<int:car_id>')
api.add_resource(CarSearchResource, '/cars/search/<string:keyword>')

# === MAIN ===
if __name__ == '__main__':
    # Pastikan tabel dibuat kalau belum ada
    with db:
        db.create_tables([TBCarsWeb], safe=True)
    app.run(host='0.0.0.0', port=5051, debug=True)
