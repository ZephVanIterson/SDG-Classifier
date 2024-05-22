

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import accuracy_score 
import numpy
from utility import *

def trainRF(repoInfo):
    x = []
    y = []
    yBin = []

    # Concatenate name, description, and topics into a single string for each data point
    for i in repoInfo:
        tempX = str(i[0]) + " " + str(i[1])  + " " + listToStringWithoutBrackets(i[3])
        x.append(tempX)

        #get SDG number out of string
        tempY = listToStringWithoutBrackets(i[9]).split(",")
        tempY = tempY[0]
        y.append(tempY)

        #convert SDG number to binary
        tempYBin = [0] * 17
        tempYBin[int(tempY)-1] = 1
        yBin.append(tempYBin)


    # Convert y to binary matrix representation
    # mlb = MultiLabelBinarizer()
    # y_bin = mlb.fit_transform(y)
    y_bin = numpy.array(yBin)

    # Feature extraction
    vectorizer = TfidfVectorizer()
    XVectors = vectorizer.fit_transform(x)

    # Split the data into train and test sets
    XTrain, XTest, yTrain, yTest = train_test_split(XVectors, y_bin, test_size=0.2, random_state=42)


    paramGrid = {'estimator__n_estimators': [10, 50, 100, 200, 500, 750, 1000,1500, 2000,3000], 'estimator__max_features': ['sqrt', 'log2']}
    grid = GridSearchCV(OneVsRestClassifier(RandomForestClassifier()), paramGrid, refit=True, verbose=0, n_jobs=-1)

    grid.fit(XTrain, yTrain)

    y_scores = grid.predict_proba(XTest)

    #y_pred = binarize(y_scores, threshold)
    threshold = 0.15 #0.2 best yet
    #0.18 gives 0.21
    #0.15 gives 0.27
    #0.1 is bad
    y_pred = (y_scores >= threshold).astype(int)

    # Evaluate the model
    accuracy = grid.score(XTest, yTest)
    print("Accuracy:", accuracy)

    accuracy = accuracy_score(yTest, y_pred)
    print("Accuracy:", accuracy)

    predictions = grid.predict(XTest)
    for i in range(10):
        print(f"Predicted: {y_pred[i]}")
        print(f"Actual:    {yTest[i]}")
    

    return grid
