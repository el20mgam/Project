import sqlite3
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)

api = Api(app)

# Function to interact with the SQLite database
def query_db(query, args=(), one=False):
    # Connect to the SQLite database
    conn = sqlite3.connect('co2_measurements_IOM.db')
    c = conn.cursor()
    c.execute(query, args)
    result = c.fetchall()
    conn.close()
    return (result[0] if result else None) if one else result

# Resource for measurements
class Measurements(Resource):
    def get(self):
        data = query_db("SELECT * FROM measurements")
        measurements_list = []
        for row in data:
            measurements_list.append({'datetime': row[0], 'co2': row[1], 'temperature': row[2], 'humidity': row[3]})

        lft_data = query_db("SELECT * FROM lft")
        lft_list = []
        for row in lft_data:
            lft_list.append(
                {'datetime': row[0], 'qr_code': row[1], 'outcome': row[2], 'control_magenta': row[3], 'test_magenta': row[4]})

        return jsonify({'measurements': measurements_list, 'lft': lft_list})


# Add the Measurements resource to the Api object at the '/data' endpoint
api.add_resource(Measurements, '/data')

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
