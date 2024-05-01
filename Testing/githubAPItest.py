#1. read in list of repos
#2. for each repo, get the repo info and readme
#3. save info to new csv? or 

import requests
import json
import base64
import csv
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC

accessToken = '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'
headers = {'Authorization': 'token ' + accessToken}
repoList = 'OSS4SG-Project-List.csv'

def getRepoList():
    # Read the list of repositories from the CSV file
    with open(repoList, 'r') as file:
        reader = csv.reader(file)
        repo_list = list(reader)

    return repo_list


def getRepoInfo(repo):

    # Make a GET request to fetch repository information
    response = requests.get('https://api.github.com/repos/'+repo[0], headers=headers)
    readme_response = requests.get('https://api.github.com/repos/'+repo[0]+'/readme', headers=headers)
    #print(response.text)

    # Check if the request was successful
    if response.status_code == 200:

            # Parse the JSON response
            repo_info = response.json()
            
            # Extract relevant information from repo_info
            repo_name = repo_info['full_name']
            description = repo_info['description']

            print(f"Repository: {repo_name}")
            print(f"Description: {description}")


    else:
        print(f"Failed to fetch repository information. Status code: {response.status_code}")


    if readme_response.status_code == 200:

        # Parse the JSON response
        readme_info = readme_response.json()

        # Extract content from the response
        content = readme_info['content']

        # Decode the base64-encoded content
        decoded_content = base64.b64decode(content).decode('utf-8')

        print(f"Readme Content:\n{decoded_content}")
    else:
        print(f"Failed to fetch README. Status code: {readme_response.status_code}")

    return repo_name, description, decoded_content


def getAllRepoInfo():
    # Get the list of repositories
    repo_list = getRepoList()

    # Initialize lists to store repository information
    repo_names = []
    repo_descriptions = []
    readme_contents = []

    # Get the information for each repository
    for repo in repo_list:
        repo_name, description, readme_content = getRepoInfo(repo)
        repo_names.append(repo_name)
        repo_descriptions.append(description)
        readme_contents.append(readme_content)

    return repo_names, repo_descriptions, readme_contents

def train_svm(X, y):
    # Feature extraction
    vectorizer = CountVectorizer()
    X_vectors = vectorizer.fit_transform(X)

    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X_vectors, y, test_size=0.2, random_state=42)

    # Train the SVM model
    svm_model = SVC(kernel='linear')
    svm_model.fit(X_train, y_train)

    # Evaluate the model
    accuracy = svm_model.score(X_test, y_test)
    print("Accuracy:", accuracy)

    return svm_model



def main():
    getAllRepoInfo()
    


if __name__ == "__main__":
    main()