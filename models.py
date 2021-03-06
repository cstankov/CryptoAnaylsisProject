from math import tanh
from matplotlib.pyplot import axis
import pandas as pd
from dataVisualization import plot_model_results
from dataVisualization import plot_overfitting_for_models
from dataVisualization import plot_linear_regression_results
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

OVERFITTING_ITERATIONS = 5

def run_all_models(eth_data, btc_data, with_hypertuning=False):
    run_main_models(eth_data, btc_data, with_hypertuning)
    run_linear_regression(eth_data, btc_data, with_hypertuning)

def run_main_models(eth_data, btc_data, with_hypertuning=False):
    ml_eth_data = eth_data.copy()
    ml_btc_data = btc_data.copy()
    ml_eth_data = ml_eth_data.drop(['Close'], axis=1)
    ml_btc_data = ml_btc_data.drop(['Close'], axis=1)
    eth_model_data = split_data(ml_eth_data)
    btc_model_data = split_data(ml_btc_data)
    random_forest(eth_model_data, btc_model_data, with_hypertuning)
    neural_network(eth_model_data, btc_model_data, with_hypertuning)
    gaussian_NB(eth_model_data, btc_model_data, with_hypertuning)

def run_linear_regression(eth_data, btc_data, with_hypertuning=False):
    lr_eth_data = eth_data.copy()
    lr_btc_data = btc_data.copy()
    lr_eth_data = lr_eth_data.drop(['High', 'Low', 'Price_change'], axis=1)
    lr_btc_data = lr_btc_data.drop(['High', 'Low', 'Price_change'], axis=1)
    eth_model_data = split_data_for_linear(lr_eth_data)
    btc_model_data = split_data_for_linear(lr_btc_data)
    linear_regression(eth_model_data, btc_model_data, with_hypertuning)

#########################################################
# Split Data

def convert_value(value):
    if value == 'Increased':
        return 1
    elif value == 'Decreased':
        return -1
    else:
        return 0

def split_data(data):
    X = data.iloc[:, data.columns != 'Price_change']
    price_change = data['Price_change']
    y = price_change.apply(convert_value)
    X_train, X_valid, y_train, y_valid = train_test_split(X, y)
    return [X_train, X_valid, y_train, y_valid]

def split_data_for_linear(data):
    X = data.iloc[:, data.columns != 'Close']
    y = data['Close']
    X_train, X_valid, y_train, y_valid = train_test_split(X, y)
    return [X_train, X_valid, y_train, y_valid]

#########################################################
# Random Forest Classifier

def random_forest(eth_data, btc_data, with_hypertuning):
    model_string = 'Random-Forest'
    if with_hypertuning:
        parameters = {
            'n_estimators':[50, 200, 350, 500], 
            'max_depth':[5, 7, 10, 12], 
            'min_samples_leaf':[1, 5, 10], 
            'min_samples_split':[2, 6, 10]
            }
        model = RandomForestClassifier()
        hyper_tuning(eth_data, model, model_string, parameters, is_btc=False)
        hyper_tuning(btc_data, model, model_string, parameters, is_btc=True)
    else:
        model_btc = RandomForestClassifier(max_depth= 5, min_samples_leaf = 1, min_samples_split = 2, n_estimators = 50)
        model_eth = RandomForestClassifier(max_depth= 10, min_samples_leaf = 10, min_samples_split = 2, n_estimators = 50)
        overfitting_points = pd.DataFrame(columns=['eth_train_acc', 'eth_valid_acc', 'btc_train_acc', 'btc_valid_acc'])
        for i in range(0, OVERFITTING_ITERATIONS):
            eth_acc = classification(eth_data, model_eth, model_string, is_btc=False)
            btc_acc = classification(btc_data, model_btc, model_string, is_btc=True)
            overfitting_points.loc[len(overfitting_points)] = [eth_acc[0], eth_acc[1], btc_acc[0], btc_acc[1]]
        plot_overfitting_for_models(overfitting_points, 'Random Forest Overfitting', 'rf-overfitting.png')

#########################################################
# Neural Network Classifier

def neural_network(eth_data, btc_data, with_hypertuning):
    model_string = 'Multi-layer_perceptron'
    if with_hypertuning:
        parameters = {
            'learning_rate_init': [0.0001, 0.001, 0.01],
            'max_iter': [300],
            'hidden_layer_sizes': [(500, 400, 300, 200, 100), (400, 400, 400, 400, 400), (300, 300, 300, 300, 300), (200, 200, 200, 200, 200)],
            'activation': ['logistic', 'tanh', 'relu'],
            'alpha': [0.0001, 0.001, 0.005],
            'early_stopping': [True, False]
            }
        model = MLPClassifier()
        hyper_tuning(eth_data, model, model_string, parameters, is_btc=False)
        hyper_tuning(btc_data, model, model_string, parameters, is_btc=True)
    else:
        model_btc = MLPClassifier(activation='logistic', alpha= 0.0001, early_stopping=True, hidden_layer_sizes= (500, 400, 300, 200, 100), learning_rate_init=0.0001, max_iter=300)
        model_eth = MLPClassifier(activation='tanh', alpha=0.005, early_stopping=True, hidden_layer_sizes=(200,200,200,200,200), learning_rate_init=0.01, max_iter=300)
        overfitting_points = pd.DataFrame(columns=['eth_train_acc', 'eth_valid_acc', 'btc_train_acc', 'btc_valid_acc'])
        for i in range(0, OVERFITTING_ITERATIONS):
            eth_acc = classification(eth_data, model_eth, model_string, is_btc=False)
            btc_acc = classification(btc_data, model_btc, model_string, is_btc=True)
            overfitting_points.loc[len(overfitting_points)] = [eth_acc[0], eth_acc[1], btc_acc[0], btc_acc[1]]
        plot_overfitting_for_models(overfitting_points, 'Neural Network Overfitting', 'nn-overfitting.png')

#########################################################
# Gaussian Naive Bayes Classifier

def gaussian_NB(eth_data, btc_data, with_hypertuning):
    model_string = 'gaussianNB'
    if with_hypertuning:
        parameters = {
            'var_smoothing': [0.000000001, 0.00000001, 0.0000001, 0.000001]
            }
        model = GaussianNB()
        hyper_tuning(eth_data, model, model_string, parameters, is_btc=False)
        hyper_tuning(btc_data, model, model_string, parameters, is_btc=True)
    else:
        model = GaussianNB()
        overfitting_points = pd.DataFrame(columns=['eth_train_acc', 'eth_valid_acc', 'btc_train_acc', 'btc_valid_acc'])
        for i in range(0, OVERFITTING_ITERATIONS):
            eth_acc = classification(eth_data, model, model_string, is_btc=False)
            btc_acc = classification(btc_data, model, model_string, is_btc=True)
            overfitting_points.loc[len(overfitting_points)] = [eth_acc[0], eth_acc[1], btc_acc[0], btc_acc[1]]
        plot_overfitting_for_models(overfitting_points, 'Gaussian Overfitting', 'gaussian-overfitting.png')

#########################################################
# Linear Regression

def linear_regression(eth_data, btc_data, with_hypertuning):
    model_string = 'linearRegression'
    if not with_hypertuning:
        model = LinearRegression()
        linear_regression_classification(eth_data, model, model_string, is_btc=False, is_linear_regression=True)
        linear_regression_classification(btc_data, model, model_string, is_btc=True, is_linear_regression=True)

#########################################################
# Classification Helper Functions

def linear_regression_classification(model_data, model, model_string, is_btc=True, is_linear_regression=False):
    X_train, X_valid, y_train, y_valid = model_data[0], model_data[1], model_data[2], model_data[3]
    feature_names = ['Open', 'Volume', 'sentiment']
    if is_btc == True:
        title = 'BTC Actual vs Prediction'
        save_fig = 'BTC-' + model_string + '-results.png'
    else:
        title = 'ETH actual vs Prediction'
        save_fig = 'ETH-' + model_string + '-results.png'
    model.fit(X_train[feature_names], y_train)
    print(model_string + " train accuracy: ", model.score(X_train[feature_names], y_train))
    print(model_string + " valid accuracy: ", model.score(X_valid[feature_names], y_valid))
    X_test = X_valid
    X_test['predictions'] = model.predict(X_valid[feature_names])
    plot_linear_regression_results(X_test, y_valid, title, save_fig)

def classification(model_data, model, model_string, is_btc=True, is_linear_regression=False):
    X_train, X_valid, y_train, y_valid = model_data[0], model_data[1], model_data[2], model_data[3]
    feature_names = ['Open', 'High', 'Low', 'Volume', 'sentiment']
    if is_btc == True:
        title = 'BTC Actual vs Prediction'
        save_fig = 'BTC-' + model_string + '-results.png'
    else:
        title = 'ETH actual vs Prediction'
        save_fig = 'ETH-' + model_string + '-results.png'
    model.fit(X_train[feature_names], y_train)
    train_acc = model.score(X_train[feature_names], y_train)
    valid_acc = model.score(X_valid[feature_names], y_valid)
    print(model_string + " train accuracy: ", train_acc)
    print(model_string + " valid accuracy: ", valid_acc)
    X_test = X_valid
    X_test['predictions'] = model.predict(X_valid[feature_names])
    if not is_linear_regression:
        get_evaluation_metrics(X_test['predictions'], y_valid)
    plot_model_results(X_test, y_valid, title, save_fig)
    return [train_acc, valid_acc]

def get_evaluation_metrics(predicted, true_values):
    target_names = ['Increased', 'Decreased']
    eval_metrics = classification_report(true_values, predicted, target_names=target_names, zero_division=1)
    print(eval_metrics)

def hyper_tuning(model_data, model, model_string, parameters, is_btc=True):
    X_train, X_valid, y_train, y_valid = model_data[0], model_data[1], model_data[2], model_data[3]
    feature_names = ['Open', 'High', 'Low', 'Volume', 'sentiment']
    gridcv = GridSearchCV(model, parameters)
    gridcv.fit(X_train[feature_names], y_train)
    print(model_string + " train accuracy: ", gridcv.score(X_train[feature_names], y_train))
    print(model_string + " valid accuracy: ", gridcv.score(X_valid[feature_names], y_valid))
    if is_btc:
        pd.DataFrame(gridcv.cv_results_).to_csv('model_data/btc_results_' + model_string + '.csv')
    else:
        pd.DataFrame(gridcv.cv_results_).to_csv('model_data/eth_results_' + model_string + '.csv')
