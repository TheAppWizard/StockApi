from flask import Flask, render_template, request, jsonify
from stock_bluprint import stock_blueprint

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(stock_blueprint)

# Sample data for usernames, passwords, and user codes
user_data = {
    "user001": {"password": "pass001", "usercode": 48273},
    "user002": {"password": "pass002", "usercode": 15947},
    "user003": {"password": "pass003", "usercode": 69351},
    "user004": {"password": "pass004", "usercode": 20486}
}

@app.route('/')
def home():
    return render_template('doc.html')

@app.route('/login', methods=['POST'])
def login():
    # Get the username and password from the request
    username = request.form.get('username')
    password = request.form.get('password')

    # Validate the username and password
    if username in user_data and user_data[username]["password"] == password:
        return jsonify({"usercode": user_data[username]["usercode"]})
    else:
        return jsonify({"error": "Kon ho aap?? Humse Kyaa Kamm, Apka kya Naam?"}), 401

if __name__ == '__main__':
    app.run(debug=True)
