import requests
import json
import base64
import csv
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import numpy

import datetime
import re


accessToken = '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'
headers = {'Authorization': 'token ' + accessToken}
repoListCSV = 'OSS4SG-Project-List-Clean.csv'
#repoListCSV = 'testdata.csv'
repoInfoCSV = 'OSS4SG-Project-Info.csv'
deletedRepos = []
pattern = re.compile('<.*?>')

def listToStringWithoutBrackets(list1):
    return str(list1).replace('[','').replace(']','')

def loadRepoList():
    # Read the list of repositories from the CSV file

    repoList = None

    #Make sure file opens correctly
    with open(repoListCSV, 'r',encoding="utf-8") as file:
        
        reader = csv.reader(file)
        repoList = list(reader)
        #skip first line for titles
        repoList = repoList[1:]

    return repoList

def loadRepoInfo():
    # Read the repository information from the CSV file
    repoInfo = None

    #Make sure file opens correctly
    with open(repoInfoCSV, 'r',encoding="utf-8") as file:
        
        reader = csv.reader(file)
        repoInfo = list(reader)
        #skip first line for titles
        repoInfo = repoInfo[1:]

    return repoInfo

def getRepoInfoFromGithub(repo):
    # Make a GET request to fetch repository information
    response = requests.get('https://api.github.com/repos/'+repo[0], headers=headers)

    repoName = repo[0]
    SDG = repo[1]
    description = ""
    decodedContent = ""
    topics = []
    lastContribution = ""
    numContributors = 0
    numStars = 0
    numSubscribers = 0
    contributorList = []


    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        repoInfo = response.json()
        
        # Extract relevant information from repoInfo
        repoName = repoInfo['full_name']
        description = repoInfo['description']
        topics = list(repoInfo['topics'])
        lastContribution = repoInfo['pushed_at']
        numStars = repoInfo['stargazers_count']
        #last_contribution_date = datetime.strptime(last_contribution, '%Y-%m-%dT%H:%M:%SZ')
        numSubscribers = repoInfo['subscribers_count']
        
        contributorsResponse = requests.get('https://api.github.com/repos/'+repo[0]+'/contributors', headers=headers)
        if contributorsResponse.status_code == 200:
            contributorsInfo = contributorsResponse.json()


            while 'next' in contributorsResponse.links:
                # Make a GET request for the next page of contributors
                next_page_url = contributorsResponse.links['next']['url']
                contributorsResponse = requests.get(next_page_url, headers={'Accept': 'application/vnd.github.v3+json'})
                
                # Check if the request was successful
                if contributorsResponse.status_code == 200:
                    # Parse the JSON response
                    additional_contributors = contributorsResponse.json()
                    
                    # Add contributors from the next page to the list
                    contributorsInfo.extend(additional_contributors)
                else:
                    #print(f"Failed to fetch contributors (next page). Status code: {contributorsResponse.status_code}")
                    break

            for contributor in contributorsInfo:
                contributorList.append((contributor['login'], contributor['contributions']))

            numContributors = len(contributorsInfo)

        else:
            print(f"Failed to fetch contributors. Status code: {contributorsResponse.status_code}")

        readmeResponse = requests.get('https://api.github.com/repos/'+repo[0]+'/readme', headers=headers)
        if readmeResponse.status_code == 200:
            readmeInfo = readmeResponse.json()
            content = readmeInfo['content']
            decodedContent = base64.b64decode(content).decode('utf-8')
            decodedContent = cleanhtml(decodedContent)

        else:
            print(f"Failed to fetch README. Status code: {readmeResponse.status_code}")
    else:
        print(f"Failed to fetch repository information. Status code: {response.status_code}")
        deletedRepos.append(repoName)
        return False

    return repoName, description, decodedContent, topics, lastContribution, numContributors, numStars, numSubscribers, contributorList, SDG

def getAllRepoInfoFromGithub():
    # Get the list of repositories
    repoList = loadRepoList()
    entries = []
    
    # Get the information for each repository
    for repo in repoList:
        entry = getRepoInfoFromGithub(repo)
        if entry:
            entries.append(entry)

    return entries


def deleteEntry(entry, csvFile):
    #delete an entry from the csv file
    with open(csvFile, 'r', newline='') as infile:
        reader = csv.reader(infile)
        rows = [row for row in reader if row != entry]

    with open(csvFile, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)        

def deleteEntries(entries, csvFile):
    #delete multiple entries from the csv file
    with open(csvFile, 'r', newline='',encoding="utf-8") as infile:
        reader = csv.reader(infile)
        rows = [row for row in reader if row not in entries]

    with open(csvFile, 'w', newline='',encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)

def clearCSV(csvFile):
    #clear the csv file
    with open(csvFile, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Repository', 'Description', 'Readme Content', 'Topics', 'Last Contribution', 'Number of Contributors', 'Number of Stars', 'Number of Subscribers', 'Contributors','SDG'])

def saveRepoInfo(repoInfo):
    # Save the repository information to the CSV file

    #Make sure not to delte any duplicates
    with open(repoInfoCSV, 'r', newline='',encoding="utf-8") as inFile:
        reader = csv.reader(inFile)
        duplicateRows = None
        duplicateRows = [row for row in reader if row in repoInfo]
        if duplicateRows:
            deleteEntries(duplicateRows, repoInfoCSV)
    with open(repoInfoCSV, 'w', newline='',encoding="utf-8") as outFile:
        writer = csv.writer(outFile)
        writer.writerow(['Repository', 'Description', 'Readme Content', 'Topics', 'Last Contribution', 'Number of Contributors', 'Number of Stars', 'Number of Subscribers', 'Contributors', 'SDG'])
        formattedRepoInfo = []
        for repo in repoInfo:
            temp = []
            temp.append(repo[0])
            temp.append(repo[1])
            temp.append(repo[2])
            temp.append(listToStringWithoutBrackets(repo[3]))
            temp.append(repo[4])
            temp.append(repo[5])
            temp.append(repo[6])
            temp.append(repo[7])
            temp.append(listToStringWithoutBrackets(repo[8]))
            temp.append(repo[9])
            formattedRepoInfo.append(temp)

        writer.writerows(formattedRepoInfo)

def getUserInfoFromGithub(user):

    # Make a GET request to fetch user information
    response = requests.get('https://api.github.com/users/'+user, headers=headers)

    userName = user
    email = ""
    location = ""
    company = ""
    numRepos = 0
    numFollowers = 0
    numFollowing = 0
    userRepos = []
    reposContributedTo = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        userInfo = response.json()
        
        # Extract relevant information from userInfo

        #Do we need any of this?
        userName = userInfo['login']
        email = userInfo['email']
        location = userInfo['location']
        company = userInfo['company']
        numRepos = userInfo['public_repos']
        numFollowers = userInfo['followers']
        numFollowing = userInfo['following']

        #List of repos
        reposResponse = requests.get('https://api.github.com/users/'+user+'/repos', headers=headers)
        if reposResponse.status_code == 200:
            repos = reposResponse.json()
            # Check if there are more pages of repositories
            while 'next' in reposResponse.links:
                # Make a GET request for the next page of repositories
                nextPageURL = reposResponse.links['next']['url']
                reposResponse = requests.get(nextPageURL, headers={'Accept': 'application/vnd.github.v3+json'})
                
                # Check if the request was successful
                if reposResponse.status_code == 200:
                    # Parse the JSON response
                    nextRepos = reposResponse.json()
                    
                    # Add repositories from the next page to the list
                    repos.extend(nextRepos)
                else:
                    print(f"Failed to fetch repository contributions (next page). Status code: {reposResponse.status_code}")
                    break
            
            for repo in repos:
                repoName = repo['name']
                userRepos.append(repoName)
        else:
            print(f"Failed to fetch user's repositories (first page). Status code: {reposResponse.status_code}")

        publicEventsResponse = requests.get('https://api.github.com/users/'+user+'/events/public', headers=headers)
        if publicEventsResponse.status_code == 200:
            publicEvents = publicEventsResponse.json()

            while 'next' in publicEventsResponse.links:
                # Make a GET request for the next page of public events
                nextPageURL = publicEventsResponse.links['next']['url']
                publicEventsResponse = requests.get(nextPageURL, headers={'Accept': 'application/vnd.github.v3+json'})
                
                # Check if the request was successful
                if publicEventsResponse.status_code == 200:
                    # Parse the JSON response
                    nextPublicEvents = publicEventsResponse.json()
                    
                    # Add public events from the next page to the list
                    publicEvents.extend(nextPublicEvents)
                else:
                    #print(f"Failed to fetch public events (next page). Status code: {publicEventsResponse.status_code}")
                    break

            for event in publicEvents:
                if event:
                    if event['type'] == 'PushEvent':
                        repoName = event['repo']['name']
                        pushDate = event['created_at']
                        reposContributedTo.append((repoName, pushDate))

    else:
        print(f"Failed to fetch user information. Status code: {response.status_code}")

    return reposContributedTo

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
        if tempY == SDG:
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
    print("Accuracy for SDG #"+SDG+":", accuracy)

    # predictions = grid.predict(XTest)
    # for i in range(10):
    #     print(f"Predicted: {predictions[i]}\tActual: {yTest[i]}")
    
    return grid

def trainSvm(repoInfo):
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

    # for i in range(10):
    #     print(y_bin[i])
    #     print(y[i])
   
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
    for i in range(10):
        print(f"Predicted: {predictions[i]}\nActual: {yTest[i]}")
    

    return grid

def cleanhtml(raw_html):
  cleantext = re.sub(pattern, '', raw_html)
  return cleantext

def main():
    print("-----------------Started-----------------")
    repoInfo = None

    #Get repo info from github for all repos on list and saved to info 
    print("Get updated from Github? (may take a while) (y/n)")
    if input() == 'y': 
        repoInfo = getAllRepoInfoFromGithub()

        print("Update saved info (y/n)") 
        if input() == 'y':
            clearCSV(repoInfoCSV)
            saveRepoInfo(repoInfo)
    else:
        repoInfo = loadRepoInfo()



    print("Train SVM (y/n)")
    svmModel = None
    if input() == 'y':
        #svmModel = trainSvm(repoInfo)
        svmModel = trainSVMFPartial(repoInfo)

    #print classified test set from 




    print("-----------Finished-------------------")




    




if __name__ == "__main__":
    main()