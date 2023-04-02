# Import liabraries

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import pickle
from firebase_admin import db
import pyrebase
import urllib
from flask import Flask , jsonify,request
import json

# flask
app = Flask(__name__)

response = ''
caloric_needs = ''
recommended_breakfast=''

     

# APPROUTING

@app.route('/name', methods = ['GET', 'POST'])
def nameRoute():

    #fetching the global response variable to manipulate inside the function
    global response
    global caloric_needs
    global recommended_breakfast

#checking the request type we get from the app
    if(request.method == 'POST'):
        request_data = request.data #getting the response data
        request_data = json.loads(request_data.decode('utf-8')) #converting it from json to key value pair
        height = int(request_data['height']) #assigning it to name
        age = int(request_data['age'])
        gender = int(request_data['gender'])
        weight = int(request_data['weight'])



        #( response = f'{height}' #re-assigning response with the name we got from the user)
# This is a SDK from firebase

        config = {
            "apiKey": "AIzaSyD4n2356evIuRlqkMuq5do3wTUzEL3kFeM",
            "authDomain": "you domain",
            "databaseURL":"https://insta-clone-c4d7e-default-rtdb.firebaseio.com",
            "projectId": "insta-clone-c4d7e",
            "storageBucket": "insta-clone-c4d7e.appspot.com",
            # Don't forget to format the "double-quotes" for the strings, firebase not make that!
            "messagingSenderId":"1094506106434",
            "appId":  "1:1094506106434:web:3dd15d07dd0a2389e527db",
  
            }   

        firebase = pyrebase.initialize_app(config)  # data from the config
        storage = firebase.storage()  # storage of database


        Food = storage.child('csv_files/foodfin.csv').get_url(None)
        Final = storage.child('csv_files/Final_Data.csv').get_url(None)
        mlpmodel = storage.child('F_MLP_model.pkl').get_url(None)


        ML = urllib.request.urlopen(mlpmodel)
        myfile = ML.read()

        # load datasets
        Food_data = pd.read_csv(Food)
        Final_data = pd.read_csv(Final)

        # Load Model
        MLP_loaded_mpdel=pd.read_pickle(mlpmodel)


        #Pipeline to standerdize data
        my_pipeline =Pipeline([
            ('std_scaler', StandardScaler()),
        ])
        my_pipeline.fit_transform(Final_data)



           
        def calculate_bmi(height, weight):
            return weight / (height / 100)**2

        # Function to calculate BMR
        def calculate_bmr(age, height, weight, gender, activity):
            if gender == 1:
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

    # if activity == 1:
    #     bmr *= 1.2
    # elif activity == 2:
    #     bmr *= 1.375
    # elif activity == 3:
    #     bmr *= 1.55
    # elif activity == 4:
    #     bmr *= 1.725
    # else:
    #     bmr *= 1.9

            return bmr

        def activity_val():
            activity = int()
            if activity == 1:
                activity_index = 1.2
            elif activity == 2:
                activity_index = 1.3
            elif activity == 3:
                activity_index = 1.5
            elif activity == 4:
                activity_index = 1.7
            else:
                activity_index = 1.9
            return activity_index

        # Take user input
       
        height_m=int(height)/100
        activity = 1.5
        bmi = calculate_bmi(height, weight)
        bmr = calculate_bmr(age, height, weight, gender, activity)

        scaler = StandardScaler()
        inputs_list = []
        inputs_list.append([age, weight, height_m, gender, bmi, bmr, activity])
        # print(inputs_list)

        Data=my_pipeline.transform(inputs_list)
        # print(test)

        STD_Data=MLP_loaded_mpdel.predict(Data)
        caloric_needs = STD_Data[0]
        # print(caloric_needs)
        # print(type(caloric_needs))

        # Divide caloric needs into breakfast, lunch, and dinner
        calories_breakfast = int(caloric_needs * 0.25)
        calories_lunch = int(caloric_needs * 0.40)
        calories_dinner = int(caloric_needs * 0.35)

        # Filter food dataset by meal type and shuffle the items
        breakfast_items = Food_data[Food_data['Breakfast'] == 1].sample(frac=1).reset_index(drop=True)
        lunch_items = Food_data[Food_data['Lunch'] == 1].sample(frac=1).reset_index(drop=True)
        dinner_items = Food_data[Food_data['Dinner'] == 1].sample(frac=1).reset_index(drop=True)

        # Recommend breakfast
        recommended_breakfast = ''
        for i, row in breakfast_items.iterrows():
            if row['Calories'] <= calories_breakfast:
                recommended_breakfast += f"\n{row}\n\n"
                calories_breakfast -= row['Calories']
            if calories_breakfast <= 0:
                break

        # Recommend lunch
        recommended_lunch = ''
        for i, row in lunch_items.iterrows():
            if row['Calories'] <= calories_lunch:
                recommended_lunch += f"\n{row}\n\n"
                calories_lunch -= row['Calories']
            if calories_lunch <= 0:
                break

        # Recommend dinner
        recommended_dinner = ''
        for i, row in dinner_items.iterrows():
            if row['Calories'] <= calories_dinner:
                recommended_dinner += f"\n{row}\n\n"
                calories_dinner -= row['Calories']
            if calories_dinner <= 0:
                break

        
        response = f"Recommended breakfast (total calories: {caloric_needs * 0.25}):{recommended_breakfast}\n"
        
        return " " #to avoid a type error 
    else:
 

# Print Recommendations
        # print(f"Recommended lunch (total calories: {caloric_needs * 0.40}):{recommended_lunch}\n")
        # print(f"Recommended dinner (total calories: {caloric_needs * 0.35}):{recommended_dinner}\n")

        return jsonify({'breakfast' : response})#sending data back to your frontend app



if __name__ =="__main__":
    app.run(debug=True)

