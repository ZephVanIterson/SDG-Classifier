
from githubscraping import * 

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




    print("-----------Finished-------------------")



if __name__ == "__main__":
    main()