import sqlite3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


def query_db(query, args=(), one=False):
    conn = sqlite3.connect('co2_measurements_IOM.db')
    c = conn.cursor()
    c.execute(query, args)
    result = c.fetchall()
    conn.close()
    return (result[0] if result else None) if one else result


class Measurements(Resource):
    def get(self):
        data = query_db("SELECT * FROM measurements")
        measurements_list = []
        for row in data:
            measurements_list.append({'datetime': row[0], 'co2': row[1], 'temperature': row[2], 'humidity': row[3]})
        return jsonify(measurements_list)


api.add_resource(Measurements, '/measurements')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
