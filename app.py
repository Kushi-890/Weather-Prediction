from flask import Flask, render_template, request
import requests
import logging
from datetime import datetime, timedelta

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

API_KEY = "1b999e347fbf498f8d373726250503"

def get_sample_data(city="Sample City"):
    """Generate sample weather data when API is unavailable"""
    current_date = datetime.now()
    return {
        "location": {
            "name": city,
            "country": "Sample Country"
        },
        "current": {
            "temp_c": 22,
            "condition": {
                "text": "Partly cloudy",
                "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"
            },
            "humidity": 65,
            "wind_kph": 15
        },
        "forecast": {
            "forecastday": [
                {
                    "date": (current_date + timedelta(days=i)).strftime("%d/%m/%Y"),
                    "day": { 
                        "maxtemp_c": 24 + i,
                        "mintemp_c": 18 + i,
                        "condition": {
                            "text": "Sunny",
                            "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png"
                        }
                    }
                }
                for i in range(7)
            ]
        }
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error = None
    
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            try:
                url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7"
                app.logger.debug(f"Requesting weather data for city: {city}")
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Convert date format for each forecast day
                for day in data['forecast']['forecastday']:
                    # Convert from YYYY-MM-DD to DD/MM/YYYY
                    original_date = datetime.strptime(day['date'], '%Y-%m-%d')
                    day['date'] = original_date.strftime('%d/%m/%Y')
                
                weather_data = data
                app.logger.debug("Successfully retrieved weather data")
            except requests.RequestException as e:
                error = f"Could not get weather data. Error: {str(e)}"
                app.logger.error(f"API request failed: {str(e)}")
                weather_data = get_sample_data(city)  # Use sample data on error
    else:
        # Show sample data on initial load
        weather_data = get_sample_data()

    return render_template('index.html', weather_data=weather_data, error=error)

if __name__ == '__main__':
    app.run(debug=True) 