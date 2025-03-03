from flask import Flask
from routes import main_blueprint

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.config['SECRET_KEY'] = 'energy_forecast_secret_key'

app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    app.run(debug=True)