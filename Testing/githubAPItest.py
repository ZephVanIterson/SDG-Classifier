import requests
import json
import base64
import csv

access_token = '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'

def main():
    # Set up the headers with the access token
    headers = {'Authorization': f'token {access_token}'}

    #Read in csv with list of repos
    with open('OSS4SG-Project-List.csv', 'r') as file:
        repos = csv.reader(file)
        for repo in repos:

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


if __name__ == "__main__":
    main()