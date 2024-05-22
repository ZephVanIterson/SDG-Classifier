from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier

from utility import *
import numpy

#Uses entire data set but only considers the four most common SDGs, all others are considered as none
def trainSVMFPartial(repoInfo):
    x = []
    y = []
    yBin = []
    count = 0
        

    # Concatenate name, description, and topics into a single string for each data point
    for i in repoInfo:
        tempX = str(i[0]) + " " + str(i[1])  + " " + listToStringWithoutBrackets(i[3])
        x.append(tempX)
        tempY = listToStringWithoutBrackets(i[9]).split(",")
        tempY = tempY[0]
        tempY = int(tempY)

        if tempY == 3:
            tempY = 1
        elif tempY == 4:
            tempY = 2
        elif tempY == 16:
            tempY = 3
        elif tempY == 17:
            tempY = 4
        else:
            tempY = 0
            count += 1

        y.append(tempY)
        tempYBin = [0] * 4
        if tempY != 0:
            tempYBin[int(tempY)-1] = 1
        yBin.append(tempYBin)


    # Convert y to binary matrix representation
    # mlb = MultiLabelBinarizer()
    # y_bin = mlb.fit_transform(y)
    y_bin = numpy.array(yBin)

    for i in range(10):
        print(y_bin[i])
        print(y[i])

    print("Count: ", count)
   
    # Feature extraction
    vectorizer = TfidfVectorizer()
    XVectors = vectorizer.fit_transform(x)

    # Split the data into train and test sets
    XTrain, XTest, yTrain, yTest = train_test_split(XVectors, y_bin, test_size=0.2, random_state=42)

    # Define parameter grid
    svcParamGrid = {'estimator__C': [0.1,0.5, 1,5, 10, 100], 'estimator__gamma': [5,1,0.5, 0.1, 0.01, 0.001], 'estimator__kernel': ['linear', 'rbf']}
    rfParamGrid = {'estimator__n_estimators': [10, 50, 100, 200, 500], 'estimator__max_features': ['auto', 'sqrt', 'log2']}

    # SVCModel = SVC(C=1, gamma=0.1, kernel='rbf')
    # RFModel = RandomForestClassifier(n_estimators=10, random_state=42)

    # OVRC = OneVsRestClassifier(SVCModel)
    # OVRC.fit(XTrain, yTrain)

    # Train the SVM model with GridSearchCV
    grid = GridSearchCV(OneVsRestClassifier(SVC()), svcParamGrid, refit=True, verbose=0, n_jobs=-1)
    #for random forest
    #grid = GridSearchCV(OneVsRestClassifier(RandomForestClassifier()), rfParamGrid, refit=True, verbose=0, n_jobs=-1)
    grid.fit(XTrain, yTrain)

    # Evaluate the model
    accuracy = grid.score(XTest, yTest)
    print("Accuracy:", accuracy)

    predictions = grid.predict(XTest)
    for i in range(50):
        print(f"Predicted: {predictions[i]}\tActual: {yTest[i]}")
    
    return grid

#Uses entire data set but only considers the specified SDG as 1, all others are considered 0
#Very high accuracy for any individual
def trainSVMForOneSDG(repoInfo, SDG):
    x = []
    y = []
    yBin = []

    # Concatenate name, description, and topics into a single string for each data point
    for i in repoInfo:
        tempX = str(i[0]) + " " + str(i[1])  + " " + listToStringWithoutBrackets(i[3])
        x.append(tempX)
        tempY = listToStringWithoutBrackets(i[9]).split(",")
        tempY = tempY[0]
        if int(tempY) == int(SDG):
            y.append(1)
        else:
            y.append(0)
   
    # Feature extraction
    vectorizer = TfidfVectorizer()
    XVectors = vectorizer.fit_transform(x)

    # Split the data into train and test sets
    XTrain, XTest, yTrain, yTest = train_test_split(XVectors, y, test_size=0.2, random_state=42)

    # Define parameter grid
    svcParamGrid = {'estimator__C': [0.1,0.5, 1,5, 10, 100], 'estimator__gamma': [5,1,0.5, 0.1, 0.01, 0.001], 'estimator__kernel': ['linear', 'rbf']}
    rfParamGrid = {'estimator__n_estimators': [10, 50, 100, 200, 500], 'estimator__max_features': ['auto', 'sqrt', 'log2']}

    # SVCModel = SVC(C=1, gamma=0.1, kernel='rbf')
    # RFModel = RandomForestClassifier(n_estimators=10, random_state=42)

    # OVRC = OneVsRestClassifier(SVCModel)
    # OVRC.fit(XTrain, yTrain)

    # Train the SVM model with GridSearchCV
    grid = GridSearchCV(OneVsRestClassifier(SVC()), svcParamGrid, refit=True, verbose=0, n_jobs=-1)
    #for random forest
    #grid = GridSearchCV(OneVsRestClassifier(RandomForestClassifier()), rfParamGrid, refit=True, verbose=0, n_jobs=-1)
    grid.fit(XTrain, yTrain)

    # Evaluate the model
    accuracy = grid.score(XTest, yTest)
    print("Accuracy for SDG #"+str(SDG)+":", accuracy)

    # predictions = grid.predict(XTest)
    # for i in range(10):
    #     print(f"Predicted: {predictions[i]}\tActual: {yTest[i]}")
    
    return grid

def trainSVM(repoInfo):
    x = []
    y = []
    yBin = []

    # Concatenate name, description, and topics into a single string for each data point
    for i in repoInfo:
        tempX = str(i[0]) + " " + str(i[1])  + " " + listToStringWithoutBrackets(i[3])
        x.append(tempX)
        tempY = listToStringWithoutBrackets(i[9]).split(",")
        tempY = tempY[0]
        y.append(tempY)
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

    paramGrid = {'estimator__C': [0.1,0.5, 1,5, 10, 100], 'estimator__gamma': [5,1,0.5, 0.1, 0.01, 0.001], 'estimator__kernel': ['linear', 'rbf']}
    grid = GridSearchCV(OneVsRestClassifier(SVC()), paramGrid, refit=True, verbose=0, n_jobs=-1)
    # elif model == 'RF':
    #     paramGrid = {'estimator__n_estimators': [10, 50, 100, 200, 500], 'estimator__max_features': ['auto', 'sqrt', 'log2']}
    #     grid = GridSearchCV(OneVsRestClassifier(RandomForestClassifier()), paramGrid, refit=True, verbose=0, n_jobs=-1)

    # Train the SVM model with GridSearchCV
    
    #for random forest
    #grid = GridSearchCV(OneVsRestClassifier(RandomForestClassifier()), rfParamGrid, refit=True, verbose=0, n_jobs=-1)
    grid.fit(XTrain, yTrain)

    # Evaluate the model
    accuracy = grid.score(XTest, yTest)
    print("Accuracy:", accuracy)

    predictions = grid.predict(XTest)
    for i in range(10):
        print(f"Predicted: {predictions[i]}\nActual: {yTest[i]}")
    

    return grid

