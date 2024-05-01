import requests
import json
import base64
import csv
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
import datetime



accessToken = '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'
headers = {'Authorization': 'token ' + accessToken}
repoListCSV = 'OSS4SG-Project-List.csv'
#repoListCSV = 'testdata.csv'
repoInfoCSV = 'OSS4SG-Project-Info.csv'
deletedRepos = []

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
        print(repoInfo)

    return repoInfo


def getRepoInfoFromFile(repo):
    # Get the repository information from the CSV file
    repoName = repo[0]
    description = repo[1]
    readmeContent = repo[2]

    # print(f"Repository: {repoName}")
    # print(f"Description: {description}")
    # print(f"Readme Content:\n{readmeContent}")

    return repoName, description, readmeContent

def getAllRepoInfo():
   
    repoList = None

    #Make sure file opens correctly
    with open(repoListCSV, 'r') as file:
        
        reader = csv.reader(file)
        repoList = list(reader)
        #skip first line for titles
        repoList = repoList[1:]

    return repoList

def getRepoInfoFromGithub(repo):
    # Make a GET request to fetch repository information
    response = requests.get('https://api.github.com/repos/'+repo[0], headers=headers)

    repoName = repo[0]
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
        topics = repoInfo['topics']
        lastContribution = repoInfo['pushed_at']
        numStars = repoInfo['stargazers_count']
        #last_contribution_date = datetime.strptime(last_contribution, '%Y-%m-%dT%H:%M:%SZ')
        numSubscribers = repoInfo['subscribers_count']
        
        contributorsResponse = requests.get('https://api.github.com/repos/'+repo[0]+'/contributors', headers=headers)
        if contributorsResponse.status_code == 200:
            contributorsInfo = contributorsResponse.json()
            numContributors = len(contributorsInfo)
            for contributor in contributorsInfo:
                contributorList.append((contributor['login'], contributor['contributions']))

        else:
            print(f"Failed to fetch contributors. Status code: {contributorsResponse.status_code}")

        readmeResponse = requests.get('https://api.github.com/repos/'+repo[0]+'/readme', headers=headers)
        if readmeResponse.status_code == 200:
            readmeInfo = readmeResponse.json()
            content = readmeInfo['content']
            decodedContent = base64.b64decode(content).decode('utf-8')

        else:
            print(f"Failed to fetch README. Status code: {readmeResponse.status_code}")
    else:
        print(f"Failed to fetch repository information. Status code: {response.status_code}")
        description = "Repository not found"
        deletedRepos.append(repoName)

    return repoName, description, decodedContent, listToStringWithoutBrackets(topics), lastContribution, numContributors, numStars, numSubscribers, listToStringWithoutBrackets(contributorList)

def getAllRepoInfoFromGithub():
    # Get the list of repositories
    repoList = loadRepoList()
    entries = []
    
    # Get the information for each repository
    for repo in repoList:
        entry = getRepoInfoFromGithub(repo)
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
        writer.writerow(['Repository', 'Description', 'Readme Content', 'Topics', 'Last Contribution', 'Number of Contributors', 'Number of Stars', 'Number of Subscribers', 'Contributors'])

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
        writer.writerow(['Repository', 'Description', 'Readme Content', 'Topics', 'Last Contribution', 'Number of Contributors', 'Number of Stars', 'Number of Subscribers', 'Contributors'])
        writer.writerows(repoInfo)

#Fix this later
def trainSvm(xName, xDesc, XReadMe, y):
    # Feature extraction
    vectorizer = CountVectorizer()
    XVectors = vectorizer.fit_transform(X)

    # Split the data into train and test sets
    XTrain, XTest, yTrain, yTest = train_test_split(XVectors, y, test_size=0.2, random_state=42)

    # Train the SVM model
    svmModel = SVC(kernel='linear')
    svmModel.fit(XTrain, yTrain)

    # Evaluate the model
    accuracy = svmModel.score(XTest, yTest)
    print("Accuracy:", accuracy)

    return svmModel

def main():
    print("Started")

    #Get repo info from github for all repos on list and saved to info 
    print("do you want to update the repo info? (y/n)")
    if input() == 'y': 
        clearCSV(repoInfoCSV)
        repoInfo = getAllRepoInfoFromGithub()
        saveRepoInfo(repoInfo)

    print(*repoInfo, sep = "\n\n\n")

    

    #Get repo info from info csv
    #repoInfo = loadRepoInfo()

    # Read the repository information from the CSV file

    




if __name__ == "__main__":
    main()