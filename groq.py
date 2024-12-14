

from crewai import Agent, Task, Crew, Process
import os

from utility import *

from githubscraping import loadRepoInfo

os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_MODEL_NAME"] = "llama3-8b-8192"

repoName = ""
repoDescription = ""
repoTags = ""
repoREADME = ""

Accuracy = 0
correct = 0
incorrect = 0
total = 0



SDGClassifier = Agent(
    role = "SDG Classifier",
    goal = "Accurately classify Open Source Projects based on which of the 17 Social Development Goal(SDG) that they adress",
    backstory = "You are an AI assistant whose goal is to classify Open Source Projects based on which of the 17 Social Development Goal(SDG) that they adress",
    verbose = True,
    allow_delegation = False
)

repoInfo = loadRepoInfo()
outputs = []

for repo in repoInfo:


    repoName = repo[0]
    repoDescription = repo[1]
    repoTags = repo[3]
    repoREADME = repo[2]


    classifyOSS = Task(


        description = f"Classify the following project based on which of the 17 Social Development Goal(SDG) that it adresses: \n\nname: {repoName}\nDescription: {repoDescription}\nTags: {repoTags}\nREADME: {repoREADME}",
        agent = SDGClassifier,
        # expected_output = "The SDG(s) that the project adresses; e.g. 'SDG 1: No Poverty', plus an explanation for why it chose it. It can select as many SDGs asapplies to the project",
        expected_output = "The number of the SDG that applies to the project; e.g. '1'. The final output should be only the integer value from 1-17 for the SDG that applies to the project. There should be ne description, explanantion, or any other text in the output. The output should be a single integer value from 1-17",

    )


    crew = Crew(
        agents = [SDGClassifier],
        tasks=[classifyOSS],
        verbose=0,

        
        process=Process.sequential

    )

    SDGLabel = stringToList(repo[13])
    SDGLabel = SDGLabel[0]

    output = crew.kickoff()
    outputs.append((output, SDGLabel))

    #Print llm output
    print("LLM Output: ", output)
    print("SDG Label: ", SDGLabel)

    if output == SDGLabel:
        print("Correct")
        correct += 1
    else:
        print("Incorrect")
        incorrect += 1

    total += 1

    Accuracy = correct/total
    print(f"Accuracy: {Accuracy}")

Accuracy = correct/total
print(f"Accuracy: {Accuracy}")
