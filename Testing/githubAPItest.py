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
#repoListCSV = 'OSS4SG-Project-List.csv'
repoListCSV = 'testdata.csv'
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

    return repoInfo

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
                    print(f"Failed to fetch contributors (next page). Status code: {contributorsResponse.status_code}")
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
                    print(f"Failed to fetch public events (next page). Status code: {publicEventsResponse.status_code}")
                    break

            for event in publicEvents:
                print(event)
                print("\n\n\n")
                if event:
                    if event['type'] == 'PushEvent':
                        repoName = event['repo']['name']
                        pushDate = event['created_at']
                        reposContributedTo.append((repoName, pushDate))

    else:
        print(f"Failed to fetch user information. Status code: {response.status_code}")

    return reposContributedTo

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
    repoInfo = None

    #Get repo info from github for all repos on list and saved to info 
    print("Get info from Github (y/n)")
    if input() == 'y': 
        repoInfo = getAllRepoInfoFromGithub()

        print("Update info (y/n)") 
        if input() == 'y':
            clearCSV(repoInfoCSV)
            saveRepoInfo(repoInfo)
    #else:
        #repoInfo = loadRepoInfo()
    
    getUserInfoFromGithub('simonv3')

    #print(*repoInfo, sep = "\n\n\n")

    

    #Get repo info from info csv
    #repoInfo = loadRepoInfo()

    # Read the repository information from the CSV file

    




if __name__ == "__main__":
    main()