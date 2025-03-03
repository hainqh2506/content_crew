from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from llm import togetherai_llm, gemini_llm
from data import ContentIdeaList, ContentResearch, ResearchSynthesis, ContentDraft, ContentFinal
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# Khởi tạo LLM
LLM = togetherai_llm
@CrewBase
class SocialContentIdeaCrew: #crew tạo ý tưởng
    """Social Content Creator crew"""
    
    # Định nghĩa config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    @agent
    def content_manager(self) -> Agent: #agent tạo ý tưởng
        return Agent(
            config=self.agents_config["content_manager"],
            llm=LLM,
            verbose=True,
            memory=True
        )

    @task
    def content_ideation_task(self) -> Task: #task tạo ý tưởng
        return Task(
            config=self.tasks_config["content_ideation_task"],
            agent=self.content_manager(),
            output_pydantic=ContentIdeaList,
            Verbose=True,
            output_file="output/idea.json" #lưu ý tưởng vào file idea.json
        )
        
    @crew
    def crew(self) -> Crew: #crew tạo ý tưởng
        """Creates the Content Creator Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
@CrewBase
class ContentCreationCrew: #crew tạo nội dung
    """Social Content Creator crew"""
       # Định nghĩa config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    #tools
    search_tool = SerperDevTool(n_results=5, search_type="search")  # tìm kiếm trên google news, search_type="search" tìm kiếm trên google
    scrape_tool = ScrapeWebsiteTool()  # lấy dữ liệu từ website
    tools = [search_tool, scrape_tool]  # danh sách các công cụ

    @agent
    def content_researcher(self) -> Agent: #agent tìm kiếm thông tin
        return Agent(
            config=self.agents_config["content_researcher"],
            llm=LLM,
            verbose=True,
            memory=True,
            tools=self.tools,
        )
    @agent
    def research_synthesizer(self) -> Agent: #agent tổng hợp thông tin
        return Agent(
            config=self.agents_config["research_synthesizer"],
            llm=LLM,
            verbose=True,
            memory=True
        )
    @agent
    def content_writer(self) -> Agent: #agent viết nội dung
        return Agent(
            config=self.agents_config["content_writer"],
            llm=LLM,
            verbose=True,
            memory=True
        )
    @agent
    def content_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_reviewer"],
            llm=LLM,
            verbose=True,
            memory=True
        )
        
    @task
    def research_task(self) -> Task: #task tìm kiếm thông tin
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.content_researcher(),
            output_pydantic=ContentResearch,
            Verbose=True,
            async_execution=True,
        )
    @task
    def research_synthesis_task(self) -> Task: #task tổng hợp thông tin
        return Task(
            config=self.tasks_config["research_synthesis_task"],
            agent=self.research_synthesizer(),
            output_pydantic=ResearchSynthesis,
            Verbose=True,
            context=[self.research_task()],
            
        ) 
        
    @task
    def content_writing_task(self) -> Task: #task viết nội dung
        return Task(
            config=self.tasks_config["content_writing_task"],
            agent=self.content_writer(),
            output_pydantic=ContentDraft,
            Verbose=True,
            context=[self.research_synthesis_task(), self.research_task()]
        )
    @task
    def content_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["content_review_task"],
            agent=self.content_reviewer(),
            Verbose=True,
            context=[self.content_writing_task()],
            #output_pydantic=ContentFinal
        )
    
           
    @crew
    def crew(self) -> Crew: #crew tạo nội dung
        """Creates the Content Creator Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm = 14,
            planning_llm = LLM,
            planning=False,
            output_log_file="output/log"
        )