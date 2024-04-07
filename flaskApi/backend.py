# app.py

from flask import Flask, request, jsonify
import pickle
import numpy as np
from flask_cors import CORS
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
import json


app = Flask(__name__)
CORS(app, supports_credentials=True)

cors=CORS(app)
CORS(app, origins='https://127.0.0.1:5000', supports_credentials=True)

data = pd.read_csv("par1final.csv")
X = data[['Air temperature | (°C)', 'Pressure | (atm)', 'Wind speed | (m/s)', 'year', 'month', 'day', 'hour',]]
y = data['Power generated by system | (MW)']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=50)

model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)
global predicted_power

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    print(data)

    temp = data['Temp']
    pressure = data['Pressure']
    windspeed = data['WindSpeed']
    year = data['Year']
    month = data['Month']
    day = data['Day']
    hour = data['Hour']
    
    
    
    
    
    new_data = pd.DataFrame({
    'Air temperature | (°C)': [temp],
    'Pressure | (atm)': [pressure],
    'Wind speed | (m/s)': [windspeed],
    'year': [year],  
    'month': [month],     
    'day': [day],       
    'hour': [hour],       
    }, index=[0])



    predicted_power = model.predict(new_data)
    data_df = pd.read_csv('grid24final.csv')
    filtered_data = data_df[(data_df['month'] == month) & 
                        (data_df['day'] == day) & 
                        (data_df['hour'] == hour)]

# Assuming there's only one matching row, extract the values of c1, c2, c3, p1, p2, p3
    if not filtered_data.empty:
        c1 = filtered_data['c1'].iloc[0]
        c2 = filtered_data['c2'].iloc[0]
        c3 = filtered_data['c3'].iloc[0]
        p1 = filtered_data['p1'].iloc[0]
        p2 = filtered_data['p2'].iloc[0]
        p3 = filtered_data['p3'].iloc[0]
    
    g1 = 0.20*predicted_power
    g2 = 0.45*predicted_power
    g3 = 0.35*predicted_power
    
    data = pd.read_csv("part2final1.csv")
    
    X = data[['p1','p2','p3','c1','c2','c3','year','month','day','hour','g1','g2','g3']]

    # Extract dependent variable (target)
    y = data['stability']

    # Initialize Logistic Regression Classifier
    logistic_classifier = LogisticRegression(max_iter=1000, random_state=10)  # You can adjust max_iter as needed

    # Fit the classifier on the data
    logistic_classifier.fit(X, y)

    # Define input values for features
    input_data = {
        'p1': [p1],
        'p2': [p2],
        'p3': [p3],
        'c1': [c1],
        'c2': [c2],
        'c3': [c3],
        'year': [year],
        'month': [month],
        'day': [day],
        'hour': [hour],
        'g1': [g1],
        'g2': [g2],
        'g3': [g3]
    }

    # Convert input data into DataFrame
    input_df = pd.DataFrame(input_data)

    # Make predictions using the trained model
    predictions = logistic_classifier.predict(input_df)
    
    # Convert NumPy array to Python list
    predictions_list = predictions.tolist()
    
    if predictions_list[0] == 1:
        stability = "Unstable"
    else:
        stability = "Stable"

    return jsonify({'predicted_stability': stability})

@app.route('/getdata', methods=['GET'])

def another_endpoint():
    # Read data from CSV file
    data = pd.read_csv("powerpredictionfinal.csv")
    
    # Extract first 50 rows
    first_50_rows = data.head(50)
    
    # Create a list of dictionaries containing date, hour, and predicted value for each row
    predictions_list = []
    for index, row in first_50_rows.iterrows():
        prediction = {
            'day': row['day'],  # Assuming 'date' is the column name for date
            'hour': row['hour'],  # Assuming 'hour' is the column name for hour
            'predicted_value': row['Predicted Power']  # Assuming 'predicted_value' is the column name for predicted value
        }
        predictions_list.append(prediction)
    
    return jsonify({'predicted_stability': predictions_list})


if __name__ == '__main__':
    app.run(debug=True)
