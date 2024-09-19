from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process

model = Ollama(model="llama3")

OSSText = ""
repoName = ""
repoDescription = ""
repoTags = ""
repoREADME = ""



SDGClassifier = Agent(
    role = "SDG Classifier",
    llm = model,
    goal = "Accurately classify Open Source Projects based on which of the 17 Social Development Goal(SDG) that they adress",
    backstory = "You are an AI assistant whose goal is to classify Open Source Projects based on which of the 17 Social Development Goal(SDG) that they adress",
    verbose = True,
    allow_delegation = False
)

classifyOSS = Task(


    description = f"Classify the followoing projects based on which of the 17 Social Development Goal(SDG) that they adress: \n\n{OSSText}",
    Agent = SDGClassifier,
    expected_output = "The SDG that the project adresses; e.g. 'SDG 1: No Poverty'",

)


crew = Crew(
    agents = [SDGClassifier],
    tasks=[classifyOSS],
    verbose=2,

    
    process=Process.sequential

)

output = crew.kickoff()

print(output)