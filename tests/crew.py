# src/social_content_creator/crew.py (ví dụ)
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, cache_handler, tool, llm, before_kickoff, after_kickoff
from memory import long_term_memory, short_term_memory
from typing import Optional
import os
import json
from datetime import datetime, timedelta
from crewai_tools import SerperDevTool , ScrapeWebsiteTool # Ví dụ công cụ tìm kiếm
from dotenv import load_dotenv
from llm import gemini_llm, togetherai_llm, gg_embedder
from crewai.agents.parser import AgentAction, AgentFinish
from crewai.agents.crew_agent_executor import ToolResult
load_dotenv()
current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
from typing import Callable, Optional
from crewai.tasks.task_output import TaskOutput
from pydantic import BaseModel, Field

#========================================================================================================================
# This will store the callback function from crewai_taipy
# output_handler: Optional[Callable] = None
# def register_output_handler(handler: Callable):
#     """Register the output handler from crewai_taipy"""
#     global output_handler
#     output_handler = handler

# def print_output(output: TaskOutput):
#     """Bridge function to call Taipy's output handler"""
#     if output_handler:
#         output_handler(output)
#     return output
#callback=print_output (set ở task)
#========================================================================================================================


#Json ouput task config================================================================================================
class Copy(BaseModel):
	"""Copy model"""
	title: str = Field(..., description="Title of the copy")
	body: str = Field(..., description="Body of the copy")
 
class CustomOutput(BaseModel):
    """Custom output model"""
    title: str = Field(..., description="Title of the output")
    body: str = Field(..., description="Body of the output")
    copy: Copy = Field(..., description="Copy of the output")

class ContentInfo(BaseModel):
    topic: Optional[str] = None
    communication_goal: Optional[str] = None
    target_audience: Optional[str] = None
    brand_information: Optional[str] = None
    style_and_tone: Optional[str] = None
    
 
 
 
 #========================================================================================================================
@CrewBase
class SocialContentCreatorCrew():
    """Social Content Creator crew"""
    
    #config==============================================================================================
    agents_config = "config/agents.yaml" # Đường dẫn đến file agents.yaml
    tasks_config = "config/tasks.yaml"   # Đường dẫn đến file tasks.yaml
    #tools================================================================================================

    # search_tool = SerperDevTool() # Ví dụ công cụ tìm kiếm
    # scrape_tool = ScrapeWebsiteTool() # Ví dụ công cụ scrape website
    #agent===============================================================================================
    @agent
    def content_manager(self) -> Agent:
        return Agent(config=self.agents_config['content_manager'],
                     tools=[],
                     llm= togetherai_llm,
                     verbose= True,
                     memory=True,
                     ) 

    @agent
    def content_researcher(self) -> Agent:
        return Agent(config=self.agents_config['content_researcher'], 
                     tools=[SerperDevTool(), ScrapeWebsiteTool()],  
                     llm=togetherai_llm,
                     verbose= True,
                     memory=True,
                     ) 
    
    @agent
    def content_summarizer(self) -> Agent:
        return Agent(config=self.agents_config['content_summarizer'], 
                     tools=[],
                     llm=togetherai_llm,
                     verbose= True,
                     memory=True,
                     )
    
    @agent
    def content_copywriter(self) -> Agent:
        return Agent(config=self.agents_config['content_copywriter'],
                     tools=[],
                     llm=togetherai_llm,
                     verbose= True,
                     memory=True,
                     )
    
    #tasks================================================================================================
    @task
    def content_management_task(self) -> Task:
        return Task(config=self.tasks_config['content_management_task'],
                    agent=self.content_manager)  

    @task
    def content_ideation_task(self) -> Task:
        return Task(config=self.tasks_config['content_ideation_task'],
                    agent=self.content_manager,
                    output_json=Copy)   

    @task
    def content_research_task(self) -> Task:
        return Task(config=self.tasks_config['content_research_task'],
                    agent=self.content_researcher,
                    context=[self.content_ideation_task()],
                    )
    
    @task
    def content_summarize_task(self) -> Task:
        return Task(config=self.tasks_config['content_summarization_task'],
                    agent=self.content_summarizer,
                    context=[self.content_research_task()],
                    )
    @task
    def content_copywrite_task(self) -> Task:
        return Task(config=self.tasks_config['content_copywrite_task'],
                    agent= self.content_copywriter,
                    context=[self.content_summarize_task(), self.content_ideation_task()],
                    )
    
    #create crew==============================================================================================

    @crew
    def crew(self) -> Crew:
        """Creates the Social Content Creator crew"""
        return Crew(
            agents=[self.content_manager(), self.content_researcher(), self.content_summarizer(), self.content_copywriter()],
            tasks=[self.content_management_task(), self.content_ideation_task(), self.content_research_task(), self.content_summarize_task(), self.content_copywrite_task
            ],
            process=Process.sequential,
            verbose=True,
            max_rpm=15,
            memory=True,
            output_log_file="output/logs.txt",
            long_term_memory=long_term_memory,
            short_term_memory=short_term_memory,
            embedder=gg_embedder,
        )
