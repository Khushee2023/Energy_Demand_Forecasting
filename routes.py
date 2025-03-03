from flask import Blueprint, render_template, request, jsonify, current_app
import os
import pandas as pd
from datetime import datetime
from model import EnergyForecastModel

main_blueprint = Blueprint('main', __name__)

energy_model = EnergyForecastModel()

@main_blueprint.route('/')
def index():

    return render_template('index.html')

@main_blueprint.route('/forecast', methods=['POST'])
def get_forecast():
   
    try:
     
        days = int(request.form.get('days', 7))
        
    
        if days < 1 or days > 30:
            return jsonify({'error': 'Days must be between 1 and 30'}), 400
    
        start_date_str = request.form.get('start_date', None)
        start_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        forecast_data = energy_model.get_forecast_data(days=days, start_date=start_date)
        
        return jsonify({
            'success': True,
            'forecast': forecast_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_blueprint.route('/model-info')
def model_info():
    

    return jsonify({
        'features': energy_model.features,
        'model_file': 'xgboost_model.pkl',
        'description': 'XGBoost energy demand forecasting model'
    })