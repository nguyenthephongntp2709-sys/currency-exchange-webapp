from flask import Flask
from routes.currency_routes import currency_bp

app = Flask(__name__)

app.register_blueprint(currency_bp)


if __name__ == "__main__":
    app.run(debug=True)