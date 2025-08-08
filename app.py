from flask import Flask

# Create Flask app instance
app = Flask(__name__)

# Define route for homepage
@app.route('/')
def hello():
    return '<h1>Hello</h1>'

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
