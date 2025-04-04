from flask import Flask, jsonify
import inventory_inserting

app = Flask(__name__)

@app.route('/')
def insert():

    return jsonify(inventory_inserting.insert_inv().to_dicts())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)