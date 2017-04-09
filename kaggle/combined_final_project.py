# W207 Final Project
# Bike Sharing Demand Kaggle Competition
# Team Members: Zach Ingbretsen, Nicholas Chen, Keri Wheatley, and Rob Mulla
# Kaggle Link: https://www.kaggle.com/c/bike-sharing-demand




##############################################
##############################################
##############################################
# BUSINESS UNDERSTANDING

# What problem are we trying solve?
# What are the relevant metrics? How much do we plan to improve them?
# What will we deliver?

# A public bicycle-sharing system is a service in which bicycles are made available for a shared use to individuals on a very short-term basis. A bike-sharing system is comprised of a network of kiosks throughout a city which allows a participant to check-out a bike at one location and return it to a different location. Participants of a bike-sharing system can rent bikes on an as-needed basis and are charged for the duration of rental. Most programs require participants to register as users prior to usage. As of December 2016, roughly 1000 cities worldwide have bike-sharing systems.
 
# Bike-sharing kiosks act as sensor networks for recording customer demand and usage patterns. For each bike rental, data is recorded for departure location, arrival location, duration of travel, and time elapsed. This data has valuable potential to researchers for studying mobility within a city. For this project, we explore customer mobility in relationship to these factors:
 
# 1.     Time of day
# 2.     Day type (workday, weekend, holiday, etc.)
# 3.     Season (Spring, Summer, Fall, Winter)
# 4.     Weather (clear, cloudy, rain, fog, snowfall, etc.)
# 5.     Temperature (actual, “feels like”)
# 6.     Humidity
# 7.     Windspeed
 
# This project explores changes in demand given changes in weather and day. Our project delivers an exploratory data analysis as well as a machine-learning model to forecast bike rental demand. Bike rental demand is measured by total rental count which is further broken down into two rental types: rentals by registered users and rentals by non-registered users.  
 
# ***Does it also predict casual and registered?***
# ***Should we include information about the RMSLE?***




##############################################
##############################################
##############################################
# DATA UNDERSTANDING

# What are the raw data sources?
# The data sources for this project are provided by kaggle. A train and test set and a example solution submission. https://www.kaggle.com/c/bike-sharing-demand

# What does each 'unit' (e.g. row) of data represent?

# What are the fields (columns)?
# Feature	Description
# datetime	hourlydate + timestamp
# season	1 = spring, 2 = summer, 3 = fall, 4 = winter
# holiday	whether the day is considered a holiday
# workingday	whether the day is neither a weekend nor holiday
# weather	1: Clear, Few clouds, Partly cloudy, Partly cloudy 2: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist 3: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds 4: A Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog
# temp	temperature in Celsius
# atemp	"feels like" temperature in Celsius
# humidity	relative humidity
# windspeed	wind speed
# casual	number of non-registered user rentals initiated
# registered	number of registered user rentals initiated
# count	number of total rentals

# EDA
	# Distribution of each feature
	# Missing values
	# Distribution of target
	# Relationships between features
	# Other idiosyncracies?

##############################################
# IMPORT THE REQUIRED MODULES
%matplotlib inline
import pandas as pd
import numpy as np
import sklearn
import matplotlib.pyplot as plt
from datetime import datetime
from pprint import pprint
from time import time
import logging
from sklearn.model_selection import train_test_split
# SK-learn libraries for learning.
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn import preprocessing

#SK-learn libraries for transformation and pre-processing
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder

# Custom classes for this assignment
import feature_engineering as fe
##############################################
# LOAD THE DATASETS
train_df = pd.read_csv('data/train.csv')
test_df = pd.read_csv('data/test.csv')

##############################################
##############################################
##############################################
# DATA PREPARATION

# What steps are taken to prepare the data for modeling?
# feature transformations? engineering?
# table joins? aggregation?
# Precise description of modeling base tables.
# What are the rows/columns of X (the predictors)?
# What is y (the target)?




##############################################
##############################################
##############################################
# MODELING
# What model are we using? Why?
# Assumptions?
# Regularization?

##############################################
# Define pipeline
categorical = ('season', 'holiday', 'workingday', )
# datetime isn't numerical, but needs to be in the numeric branch
numerical = ('datetime', 'weather', 'temp', 'atemp', 'humidity', 'windspeed',)
pipeline = Pipeline([
    # process cat & num separately, then join back together
    ('union', FeatureUnion([ 
        ('categorical', Pipeline([
            ('select_cat', fe.SelectCols(cols = categorical)),
            ('onehot', OneHotEncoder()),    
        ])),    
        ('numerical', Pipeline([
            ('select_num', fe.SelectCols(cols = numerical)),
            ('date', fe.DateFormatter()),
            ('drop_datetime', fe.SelectCols(cols = ('datetime'), invert = True)),
            ('temp', fe.ProcessNumerical(cols_to_square = ('temp', 'atemp', 'humidity'))),
            # ('bad_weather', fe.BinarySplitter(col = 'weather', threshold = 2)),
            # ('filter', fe.PassFilter(col='atemp', lb = 15, replacement_style = 'mean'))
            ('scale', StandardScaler()),    
        ])),    
    ])),
    ('to_dense', preprocessing.FunctionTransformer(lambda x: x.todense(), accept_sparse=True)), 
    ('clf', GradientBoostingRegressor(n_estimators=100)),
])

#Helper function to calculate root mean squared error
def get_RMSE(actual_values, predicted_values):
    n = len(actual_values)
    RMSE = np.sqrt(np.sum(((np.log(predicted_values + 1) - np.log(actual_values + 1)) ** 2) / n))
    return RMSE

##############################################
# Parameters

parameters = {
    'clf__n_estimators': (50,75,100,),
    'clf__learning_rate': (0.1, 0.05, 0.01,),
    'clf__max_depth': (10, 15, 20,),
    'clf__min_samples_leaf': (3, 5, 10, 20,),
}

features = ['season', 'holiday', 'workingday', 'weather',
        'temp', 'atemp', 'humidity', 'windspeed', 'year',
         'month', 'weekday', 'hour']

##############################################
# Split into Dev and Train data and find best parameters
train_data = train_df[pd.DatetimeIndex(train_df['datetime']).day <= 16]
dev_data = train_df[pd.DatetimeIndex(train_df['datetime']).day > 16]


# I ran the full parameter list above and got these parameters. Tooks hours to run full list.
parameters = {
    'clf__n_estimators': (50,),
    'clf__learning_rate': (0.05,),
    'clf__max_depth': (15,),
    'clf__min_samples_leaf': (20,),
}
print "GridSearch for Casual rides"
casual_gs = GridSearchCV(pipeline, parameters, n_jobs=4, verbose=1)
casual_gs.fit(train_data[features], train_data['casual'])
casual_best_param = casual_gs.best_estimator_.get_params()
print "Best parameteres for casual " + casual_best_param
casual_predicted_y = casual_gs.predict(dev_data[features])
casual_rmse = get_RMSE(actual_values = train_data['casual'], predicted_values = casual_predicted_y)
print "Casual RMSE " + casual_rmse


# I ran the full parameter list above and got these parameters. Tooks hours to run full list.
parameters = {
    'clf__n_estimators': (75,),
    'clf__learning_rate': (0.01,),
    'clf__max_depth': (20,),
    'clf__min_samples_leaf': (20,),
}
print "GridSearch for Registered rides"
registered_gs = GridSearchCV(pipeline, parameters, n_jobs=4, verbose=1)
registered_gs.fit(train_data[features], train_data['registered'])
registered_best_param = registered_gs.best_estimator_.get_params()
print "Best parameteres for registered " + casual_best_param
registered_predicted_y = registered_gs.predict(dev_data[features])
registered_rmse = get_RMSE(actual_values = train_data['registered'], predicted_values = registered_predicted_y)
print "Registered RMSE " + casual_rmse

##############################################
# Create full model using all train data

casual_best_param = {
    'clf__n_estimators': (50,),
    'clf__learning_rate': (0.05,),
    'clf__max_depth': (15,),
    'clf__min_samples_leaf': (20,),
}

registered_best_param = {
    'clf__n_estimators': (75,),
    'clf__learning_rate': (0.01,),
    'clf__max_depth': (20,),
    'clf__min_samples_leaf': (20,),
}

full_casual_gs = GridSearchCV(pipeline, casual_best_param, n_jobs=4, verbose=1)
full_casual_gs.fit(train_df[features], train_df['casual'])
full_casual_predicted_y = full_casual_gs.predict(test_df[features])

full_registered_gs = GridSearchCV(pipeline, registered_best_param, n_jobs=4, verbose=1)
full_registered_gs.fit(train_df[features], train_df['registered'])
full_registered_predicted_y = full_registered_gs.predict(test_df[features])


##############################################
# Create CSV for submission

test_df.set_index(pd.DatetimeIndex(test_df['datetime']), inplace=True)
test_df['count'] = full_casual_predicted_y + full_registered_predicted_y
test_df[['count']].to_csv('data/combined_preds.csv')

# test_df['count'] = preds_count
# test_df[['count']].to_csv('data/count_preds.csv')

##############################################
##############################################
##############################################
# EVALUATION
# How well does the model perform?
# Accuracy
# ROC curves
# Cross-validation
# other metrics? performance?
# AB test results (if any)




##############################################
##############################################
##############################################
# DEPLOYMENT
# How is the model deployed?
# prediction service?
# serialized model?
# regression coefficients?
# What support is provided after initial deployment?

