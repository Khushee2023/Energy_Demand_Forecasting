import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.dates import DateFormatter
import matplotlib
matplotlib.use('Agg')  

class EnergyForecastModel:
    def __init__(self, model_path='xgboost_model.pkl'):
    
        self.model = xgb.XGBRegressor()
        self.model.load_model(model_path)
        self.features = ['dayofyear', 'hour', 'dayofweek', 'quarter', 'month', 'year']
        
    def create_features(self, df):
    
        df = df.copy()
        df['hour'] = df.index.hour
        df['dayofweek'] = df.index.dayofweek
        df['quarter'] = df.index.quarter
        df['month'] = df.index.month
        df['year'] = df.index.year
        df['dayofyear'] = df.index.dayofyear
        df['dayofmonth'] = df.index.day
        df['weekofyear'] = df.index.isocalendar().week
        return df
    
    def generate_forecast(self, days=7, start_date=None):
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
        future_dates = pd.date_range(start=start_date, periods=days*24, freq='H')
    
        future_df = pd.DataFrame(index=future_dates)
        future_df = self.create_features(future_df)
    
        X_future = future_df[self.features]
        future_df['prediction'] = self.model.predict(X_future)
        
        return future_df
    
    def get_peak_demand(self, forecast_df):
        forecast_df = forecast_df.copy()
        forecast_df['date'] = forecast_df.index.date
        
       
        peak_indices = forecast_df.groupby('date')['prediction'].idxmax()
        
       
        peak_demand_df = forecast_df.loc[peak_indices, ['prediction']].copy()
        peak_demand_df['hour'] = peak_demand_df.index.hour
        peak_demand_df['formatted_date'] = peak_demand_df.index.strftime('%Y-%m-%d')
        peak_demand_df['day_name'] = peak_demand_df.index.day_name()
        
        
        peak_demand_df['message'] = peak_demand_df.apply(
            lambda row: f"Peak demand on {row.day_name}: {row.prediction:.2f} MW at {row.hour}:00",
            axis=1
        )
        
        return peak_demand_df
    
    def generate_forecast_plot(self, forecast_df):
    
        fig, ax = plt.subplots(figsize=(10, 6))
    
        forecast_df['prediction'].plot(ax=ax, marker='o', linestyle='-', color='#1f77b4', alpha=0.8)
        
        peak_demand_df = self.get_peak_demand(forecast_df)
        ax.scatter(peak_demand_df.index, peak_demand_df['prediction'], 
                 color='red', s=80, zorder=5, label='Peak Demand')
        
        ax.set_title('Energy Demand Forecast (Next Days)', fontsize=16)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Energy Demand (MW)', fontsize=12)
        
        date_format = DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        
        ax.grid(True, alpha=0.3)
    
        ax.legend()
        
    
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def get_forecast_data(self, days=7, start_date=None):
    
        forecast_df = self.generate_forecast(days, start_date)
        
        peak_demand_df = self.get_peak_demand(forecast_df)
        
        plot_base64 = self.generate_forecast_plot(forecast_df)
        
        forecast_data = forecast_df.reset_index()
        forecast_data['datetime'] = forecast_data['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
        forecast_json = forecast_data[['datetime', 'prediction']].to_dict(orient='records')
        
        peak_demand_json = peak_demand_df.reset_index()
        peak_demand_json['datetime'] = peak_demand_json['index'].dt.strftime('%Y-%m-%d %H:%M:%S')
        peak_demand_json = peak_demand_json[['datetime', 'prediction', 'hour', 'message']].to_dict(orient='records')
        
        return {
            'forecast': forecast_json,
            'peak_demand': peak_demand_json,
            'plot': plot_base64
        }

if __name__ == "__main__":
    model = EnergyForecastModel()
    forecast_data = model.get_forecast_data(days=7)
    print(f"Generated forecast for {len(forecast_data['forecast'])} hours")
    print(f"Peak demand messages:")
    for peak in forecast_data['peak_demand']:
        print(peak['message'])