import gradio as gr
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError, Field
from crewai.flow import Flow, listen, start, persist, router, or_
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from langchain_openai import ChatOpenAI
from llm import togetherai_llm
from datetime import datetime
import json

# --- Định nghĩa Models ---
class ContentIdea(BaseModel):
    title: str = Field(description="Tiêu đề ý tưởng")
    description: str = Field(description="Mô tả ngắn gọn về ý tưởng")
    content_type: str = Field(description="Loại nội dung (bài viết, hình ảnh, video, v.v.)")
    reason: str = Field(description="Lý do ý tưởng phù hợp với mục tiêu và đối tượng")

class ContentResearch(BaseModel):
    keywords: List[str] = Field(description="Các từ khóa liên quan")
    competitor_analysis: str = Field(description="Phân tích đối thủ cạnh tranh")
    trending_topics: List[str] = Field(description="Các chủ đề đang thịnh hành")
    insights: str = Field(description="Hiểu biết và phát hiện từ nghiên cứu")

class ContentDraft(BaseModel):
    title: str = Field(description="Tiêu đề nội dung")
    body: str = Field(description="Nội dung chính")
    hashtags: List[str] = Field(description="Hashtags liên quan")
    call_to_action: str = Field(description="Kêu gọi hành động")

class ContentInfo(BaseModel):
    topic: Optional[str] = Field(default=None, description="Chủ đề của nội dung")
    communication_goal: Optional[str] = Field(default=None, description="Mục tiêu truyền thông")
    target_audience: Optional[str] = Field(default=None, description="Đối tượng mục tiêu")
    brand_information: Optional[str] = Field(default=None, description="Thông tin thương hiệu")
    style_and_tone: Optional[str] = Field(default=None, description="Phong cách và giọng điệu")


# Thêm mô hình Pydantic mới cho dữ liệu tổng hợp nghiên cứu
class ResearchSynthesis(BaseModel):
    key_insights: List[str] = Field(description="Các insight chính từ dữ liệu")
    unique_angle: str = Field(description="Góc nhìn độc đáo để tiếp cận chủ đề")
    key_elements: List[str] = Field(description="Các yếu tố quan trọng cần đưa vào nội dung")
    recommendations: List[str] = Field(description="Đề xuất cụ thể cho quá trình viết nội dung")

# Cập nhật ChatState để thêm trường synthesis_data
class ChatState(BaseModel):
    message: Optional[str] = Field(default=None, description="Nội dung tin nhắn hiện tại")
    history: Optional[str] = Field(default=None, description="Lịch sử chat")
    content_info: ContentInfo = Field(default_factory=ContentInfo)
    content_ideas: List[ContentIdea] = Field(default_factory=list, description="Ý tưởng nội dung")
    selected_idea_index: Optional[int] = Field(default=None, description="Chỉ số ý tưởng được chọn")
    research_data: Optional[ContentResearch] = Field(default=None, description="Dữ liệu nghiên cứu")
    synthesis_data: Optional[ResearchSynthesis] = Field(default=None, description="Dữ liệu tổng hợp nghiên cứu")
    content_draft: Optional[ContentDraft] = Field(default=None, description="Bản thảo nội dung")
    final_content: Optional[str] = Field(default=None, description="Nội dung cuối cùng")
    current_step: str = Field(default="start", description="Bước hiện tại trong quy trình")
    is_complete: bool = Field(default=False, description="Trạng thái hoàn thành")

    def json_serializable(self):
        data = self.model_dump()
        data["content_info"] = self.content_info.model_dump()
        if self.research_data:
            data["research_data"] = self.research_data.model_dump()
        if self.synthesis_data:
            data["synthesis_data"] = self.synthesis_data.model_dump()
        if self.content_draft:
            data["content_draft"] = self.content_draft.model_dump()
        return data

# --- CrewAI Agents và Tasks ---
@CrewBase
class SocialContentIdeaCrew:
    """Social Content Idea crew generates content ideas based on user inputs"""
    
    # Định nghĩa config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def content_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["content_manager"],
            llm=togetherai_llm,
            verbose=True,
            memory=True
        )

    @task
    def content_ideation_task(self) -> Task:
        return Task(
            config=self.tasks_config["content_ideation_task"],
            agent=self.content_manager(),
            output_pydantic=List[ContentIdea]
        )
        
    @crew
    def crew(self) -> Crew:
        """Creates the Content Idea Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

@CrewBase
class SocialContentResearchCrew:
    """Social Content Research crew performs market research"""
    
    # Định nghĩa config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def research_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["content_researcher"],
            llm=togetherai_llm,
            verbose=True,
            memory=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.research_specialist(),
            output_pydantic=ContentResearch
        )
        
    @crew
    def crew(self) -> Crew:
        """Creates the Content Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
# Thêm Crew mới cho quá trình tổng hợp nghiên cứu
@CrewBase
class SocialContentSynthesisCrew:
    """Social Content Synthesis crew synthesizes research data"""
    
    # Định nghĩa config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def research_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config["research_synthesizer"],
            llm=togetherai_llm,
            verbose=True,
            memory=True
        )

    @task
    def research_synthesis_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_synthesis_task"],
            agent=self.research_synthesizer(),
            output_pydantic=ResearchSynthesis
        )
        
    @crew
    def crew(self) -> Crew:
        """Creates the Content Synthesis Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

@CrewBase
class SocialContentWriterCrew:
    """Social Content Writer crew creates the actual content"""
    
    # Định nghĩa config files
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_writer"],
            llm=togetherai_llm,
            verbose=True,
            memory=True
        )

    @task
    def content_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["content_writing_task"],
            agent=self.content_writer(),
            output_pydantic=ContentDraft
        )
        
    @crew
    def crew(self) -> Crew:
        """Creates the Content Writer Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

@CrewBase
class SocialContentReviewCrew:
    """Social Content Review crew reviews and finalizes content"""
    
    # Định nghĩa config files
    agents_config = "config/agents.yaml" 
    tasks_config = "config/tasks.yaml"

    @agent
    def content_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_reviewer"],
            llm=togetherai_llm,
            verbose=True,
            memory=True
        )

    @task
    def content_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["content_review_task"],
            agent=self.content_reviewer()
        )
        
    @crew
    def crew(self) -> Crew:
        """Creates the Content Review Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

@persist()
class ContentChatFlow(Flow[ChatState]):
    def __init__(self, persistence=None):
        super().__init__(persistence=persistence)
        # Khởi tạo các crews
        self.content_idea_crew = SocialContentIdeaCrew().crew()
        self.content_research_crew = SocialContentResearchCrew().crew()
        self.content_writer_crew = SocialContentWriterCrew().crew()
        self.content_review_crew = SocialContentReviewCrew().crew()
        self.current_date = datetime.now().strftime("%Y-%m-%d-%H-%M")

    @start()
    def start_flow(self):
        """Bắt đầu luồng xử lý, hiển thị trạng thái hiện tại"""
        print("Bắt đầu quy trình tạo nội dung")
        print("Thông tin nội dung:", self.state.content_info)
        self.state.current_step = "ideation"
        response = "Tôi sẽ giúp bạn tạo nội dung dựa trên thông tin bạn đã cung cấp. Đang bắt đầu quá trình tạo ý tưởng..."
        return response
    
    @listen(start_flow)
    def generate_content_ideas(self):
        """Tạo ý tưởng nội dung dựa trên thông tin người dùng cung cấp"""
        print("Đang tạo ý tưởng nội dung...")
        
        inputs = {
            "message": self.state.message,
            "content_info": self.state.content_info.model_dump(),
            "history": self.state.history,
            "current_date": self.current_date
        }
        
        result = self.content_idea_crew.kickoff(inputs=inputs)
        
        if hasattr(result, 'pydantic'):
            self.state.content_ideas = result.pydantic
            print(f"Đã tạo {len(self.state.content_ideas)} ý tưởng nội dung")
            
            # Chuẩn bị phản hồi cho người dùng
            ideas_text = ""
            for i, idea in enumerate(self.state.content_ideas):
                ideas_text += f"\n\n{i+1}. **{idea.title}**\n"
                ideas_text += f"   - Loại nội dung: {idea.content_type}\n"
                ideas_text += f"   - Mô tả: {idea.description}\n"
                ideas_text += f"   - Lý do: {idea.reason}"
            
            response = f"Tôi đã tạo {len(self.state.content_ideas)} ý tưởng nội dung dựa trên thông tin bạn cung cấp:{ideas_text}\n\nBạn muốn chọn ý tưởng nào để tiếp tục? (Vui lòng nhập số thứ tự từ 1-{len(self.state.content_ideas)})"
            
            self.state.current_step = "select_idea"
            return response
        else:
            print("Không thể tạo ý tưởng nội dung")
            return "Rất tiếc, tôi không thể tạo ý tưởng nội dung. Vui lòng cung cấp thêm thông tin và thử lại."
    
    @router(generate_content_ideas)
    def process_user_selection(self):
        """Xử lý lựa chọn của người dùng về ý tưởng nội dung"""
        if self.state.current_step != "select_idea":
            return self.state.current_step
            
        try:
            # Cố gắng phân tích số từ tin nhắn người dùng
            user_message = self.state.message
            
            # Tìm số trong tin nhắn
            import re
            numbers = re.findall(r'\d+', user_message)
            
            if numbers:
                selected_index = int(numbers[0]) - 1  # Chuyển từ 1-based sang 0-based index
                
                if 0 <= selected_index < len(self.state.content_ideas):
                    self.state.selected_idea_index = selected_index
                    selected_idea = self.state.content_ideas[selected_index]
                    
                    response = f"Bạn đã chọn ý tưởng: **{selected_idea.title}**. Tôi sẽ bắt đầu nghiên cứu để phát triển nội dung này."
                    print(f"Người dùng đã chọn ý tưởng: {selected_idea.title}")
                    
                    self.state.current_step = "research"
                    return "research"
                else:
                    print(f"Lựa chọn không hợp lệ: {selected_index+1}, yêu cầu từ 1-{len(self.state.content_ideas)}")
                    return "invalid_selection"
            else:
                print("Không tìm thấy số trong tin nhắn của người dùng")
                return "invalid_selection"
                
        except Exception as e:
            print(f"Lỗi khi xử lý lựa chọn: {e}")
            return "invalid_selection"
    
    @listen("invalid_selection")
    def handle_invalid_selection(self):
        """Xử lý khi người dùng chọn không hợp lệ"""
        response = f"Vui lòng chọn một số từ 1 đến {len(self.state.content_ideas)} để tiếp tục."
        self.state.current_step = "select_idea"  # Vẫn giữ ở bước chọn ý tưởng
        return response
    
    @listen("research")
    def conduct_research(self):
        """Tiến hành nghiên cứu cho ý tưởng được chọn"""
        print("Đang tiến hành nghiên cứu...")
        
        selected_idea = self.state.content_ideas[self.state.selected_idea_index]
        
        inputs = {
            "content_info": self.state.content_info.model_dump(),
            "selected_idea": selected_idea.model_dump(),
            "current_date": self.current_date
        }
        
        result = self.content_research_crew.kickoff(inputs=inputs)
        
        if hasattr(result, 'pydantic'):
            self.state.research_data = result.pydantic
            print("Nghiên cứu hoàn tất")
            
            keywords_text = ", ".join(self.state.research_data.keywords)
            trending_topics_text = ", ".join(self.state.research_data.trending_topics)
            
            response = f"Tôi đã hoàn thành nghiên cứu cho ý tưởng **{selected_idea.title}**.\n\n"
            response += f"**Từ khóa quan trọng:** {keywords_text}\n\n"
            response += f"**Chủ đề đang thịnh hành:** {trending_topics_text}\n\n"
            response += f"**Phân tích đối thủ:** {self.state.research_data.competitor_analysis}\n\n"
            response += f"**Hiểu biết chính:** {self.state.research_data.insights}\n\n"
            response += "Bây giờ tôi sẽ bắt đầu viết nội dung dựa trên những thông tin này. Vui lòng đợi một chút..."
            
            self.state.current_step = "writing"
            return response
        else:
            print("Không thể hoàn thành nghiên cứu")
            return "Rất tiếc, tôi không thể hoàn thành nghiên cứu. Vui lòng thử lại sau."
    
    @listen(conduct_research)
    def write_content(self):
        """Viết nội dung dựa trên ý tưởng và nghiên cứu"""
        print("Đang viết nội dung...")
        
        selected_idea = self.state.content_ideas[self.state.selected_idea_index]
        
        inputs = {
            "content_info": self.state.content_info.model_dump(),
            "selected_idea": selected_idea.model_dump(),
            "research_data": self.state.research_data.model_dump(),
            "current_date": self.current_date
        }
        
        result = self.content_writer_crew.kickoff(inputs=inputs)
        
        if hasattr(result, 'pydantic'):
            self.state.content_draft = result.pydantic
            print("Bản thảo nội dung đã được tạo")
            
            response = f"Tôi đã hoàn thành bản thảo nội dung cho **{selected_idea.title}**.\n\n"
            response += f"**Tiêu đề:** {self.state.content_draft.title}\n\n"
            response += f"**Nội dung:**\n{self.state.content_draft.body}\n\n"
            response += f"**Hashtags:** {', '.join(self.state.content_draft.hashtags)}\n\n"
            response += f"**Kêu gọi hành động:** {self.state.content_draft.call_to_action}\n\n"
            response += "Bạn muốn tôi điều chỉnh nội dung này không? Nếu có, hãy cho tôi biết những thay đổi cụ thể. Nếu bạn hài lòng, hãy gõ 'OK' để tôi hoàn thiện nó."
            
            self.state.current_step = "review"
            return response
        else:
            print("Không thể tạo bản thảo nội dung")
            return "Rất tiếc, tôi không thể tạo bản thảo nội dung. Vui lòng thử lại sau."
    
    @router(write_content)
    def process_review_feedback(self):
        """Xử lý phản hồi của người dùng về bản thảo"""
        if self.state.current_step != "review":
            return self.state.current_step
            
        user_message = self.state.message.lower()
        
        if user_message in ["ok", "okay", "yes", "đồng ý", "tốt", "được"]:
            print("Người dùng chấp nhận bản thảo")
            self.state.current_step = "finalize"
            return "finalize"
        else:
            print("Người dùng yêu cầu chỉnh sửa")
            self.state.current_step = "revise"
            return "revise"
    
    @listen("revise")
    def revise_content(self):
        """Chỉnh sửa nội dung dựa trên phản hồi của người dùng"""
        print("Đang chỉnh sửa nội dung...")
        
        inputs = {
            "content_info": self.state.content_info.model_dump(),
            "content_draft": self.state.content_draft.model_dump(),
            "feedback": self.state.message,
            "current_date": self.current_date
        }
        
        result = self.content_writer_crew.kickoff(inputs=inputs)
        
        if hasattr(result, 'pydantic'):
            self.state.content_draft = result.pydantic
            print("Bản thảo nội dung đã được chỉnh sửa")
            
            response = f"Tôi đã chỉnh sửa bản thảo theo ý kiến của bạn.\n\n"
            response += f"**Tiêu đề:** {self.state.content_draft.title}\n\n"
            response += f"**Nội dung:**\n{self.state.content_draft.body}\n\n"
            response += f"**Hashtags:** {', '.join(self.state.content_draft.hashtags)}\n\n"
            response += f"**Kêu gọi hành động:** {self.state.content_draft.call_to_action}\n\n"
            response += "Bạn có hài lòng với phiên bản này không? Nếu có, hãy gõ 'OK'. Nếu không, hãy tiếp tục cung cấp phản hồi để tôi chỉnh sửa thêm."
            
            self.state.current_step = "review"
            return response
        else:
            print("Không thể chỉnh sửa bản thảo")
            return "Rất tiếc, tôi không thể chỉnh sửa bản thảo. Vui lòng thử lại sau."
    
    @listen("finalize")
    def finalize_content(self):
        """Hoàn thiện nội dung cuối cùng"""
        print("Đang hoàn thiện nội dung...")
        
        inputs = {
            "content_info": self.state.content_info.model_dump(),
            "content_draft": self.state.content_draft.model_dump(),
            "research_data": self.state.research_data.model_dump(),
            "current_date": self.current_date
        }
        
        result = self.content_review_crew.kickoff(inputs=inputs)
        
        self.state.final_content = result.raw
        print("Nội dung cuối cùng đã được hoàn thiện")
        
        response = f"Tôi đã hoàn thiện nội dung cuối cùng.\n\n{self.state.final_content}\n\n"
        response += "Cảm ơn bạn đã sử dụng dịch vụ tạo nội dung của chúng tôi! Bạn có thể lưu nội dung này hoặc bắt đầu một dự án mới."
        
        self.state.current_step = "complete"
        self.state.is_complete = True
        return response

def kickoff():
    """
    Run the flow.
    """
    lead_score_flow = ContentChatFlow()
    lead_score_flow.kickoff()


def plot():
    """
    Plot the flow.
    """
    lead_score_flow = ContentChatFlow()
    lead_score_flow.plot()


if __name__ == "__main__":
    kickoff()
    plot()