
from githubscraping import * 
#INCLUDE MODELS (llm.py, svm.py, etc)
#import LLM
import SVM
#import groq
import RandomForest
import utility



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


    #Train and test models
    print("Train and test models? (y/n)")
    if input() == 'y':
        print("Training Random Forest")
        RandomForest.trainRF(repoInfo)
        print("Training SVM")
        SVM.trainSVM(repoInfo)

        #llm runs from its own file


        #test models
        print("Testing Random Forest")
        RandomForest.testRF(repoInfo)
        print("Testing SVM")
        SVM.testSVM(repoInfo)



    print("-----------Finished-------------------")



if __name__ == "__main__":
    main()