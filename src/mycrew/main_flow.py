import warnings
from datetime import datetime
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
import uuid
from crewai.flow import Flow, listen, start, persist, router, or_
import os
import pandas as pd
from datetime import datetime
from data import ChatState, ContentInfo # import các kiểu dữ liệu
from content_crew import SocialContentIdeaCrew, ContentCreationCrew # nhóm lên ý tưởng and nhóm tạo nội dung
import mlflow

# mlflow.crewai.autolog()
# # Optional: Set a tracking URI and an experiment name if you have a tracking server
# mlflow.set_tracking_uri("http://localhost:5000") # cách chạy UI trên máy: mlflow server  
# mlflow.set_experiment("CrewAI")

from langtrace_python_sdk import langtrace
langtrace.init(api_key = '6a54ae8a80bdcbe19379319fbd08d71e246a2a2a3408cedb459067024c01c04a')

@persist()
class ContentChatFlow(Flow[ChatState]):
    def __init__(self, persistence=None):
        super().__init__(persistence=persistence)
        # Khởi tạo các nhóm
        self.content_idea_crew = SocialContentIdeaCrew().crew()
        self.content_creation_crew = ContentCreationCrew().crew()
        self.current_date = datetime.now().strftime("%Y-%m-%d-%H-%M")
        #print(f"====================INFO: __init__ class ContentChatFlow state, self.state.model_dump(): {self.state.model_dump()}")
    @start()
    def start_flow(self):
        print("\n====================DEBUG: Starting start_flow")
        print("\n====================Thông tin nội dung @start, self.state.content_info:", self.state.content_info)
        self.state.current_step = "ideation"
        #print(f"\n====================INFO: Updated state after start_flow, self.state.model_dump(): {self.state.model_dump()}")
        response = "\n====================Tôi sẽ giúp bạn tạo nội dung dựa trên thông tin bạn đã cung cấp. Đang bắt đầu quá trình tạo ý tưởng..."
        return response
    
    @listen(start_flow)
    def generate_content_ideas(self):
        print("\n\n\n====================DEBUG: Starting generate_content_ideas")
        #print(f"INFO: Current state before crew kickoff: {self.state.model_dump()}")
        print("\n====================Đang tạo ý tưởng nội dung...")
        recent_history = self.state.history[-6:] if len(self.state.history) >= 6 else self.state.history
        inputs = {
            "message": self.state.message,
            "content_info": self.state.content_info,
            "history": recent_history,
            "current_date": self.current_date
        }
        print(f"\nINFO: Inputs for crew: {inputs}")
        result =  self.content_idea_crew.kickoff(inputs=inputs)
        print(f"\n====================DEBUG: result.pydantic type: {type(result.pydantic)}")
        #print(f"\n====================DEBUG: result.pydantic value: {result.pydantic}")  
        #print(f"\n====================INFO: Crew result.raw value: {result.raw}")
        if hasattr(result.pydantic, 'ideas'):
            self.state.content_ideas = [idea.model_dump() for idea in result.pydantic.ideas]
            ideas_text = ""
            for i, idea in enumerate(self.state.content_ideas):
                ideas_text += f"\n\n{i+1}. **{idea['title']}**\n"
                ideas_text += f"   - Loại nội dung: {idea['content_type']}\n"
                ideas_text += f"   - Mô tả: {idea['description']}\n"
                ideas_text += f"   - Lý do: {idea['reason']}"
            
            # Lưu ý tưởng vào file CSV
            df = pd.DataFrame(self.state.content_ideas)
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            csv_filename = f"{output_dir}/content_ideas_{self.current_date}.csv"
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                
            response = f"\nTôi đã tạo ý tưởng nội dung dựa trên thông tin bạn cung cấp:{ideas_text}\n\nCác ý tưởng đã được lưu vào file: {csv_filename}\n\n"
            #print(f"\n====================DEBUG: response list idea content: {response}")
            self.state.temp += f"\n{response}"
            #return response
        else:
            print("\n====================Không thể tạo ý tưởng nội dung")
            return "failed"
    @listen(generate_content_ideas)
    def start_research_write(self):
        print("\n====================DEBUG: Hoàn thành generate_content_ideas")
        self.state.current_step = "start_research"

        # Lấy 3 cặp trò chuyện gần nhất (6 tin nhắn)
        recent_history = self.state.history[-6:] if len(self.state.history) >= 6 else self.state.history

        inputs = {
            "message": self.state.message,
            "history": recent_history,  # Sử dụng history đã được cắt gọn
            "content_info": self.state.content_info,
            "current_date": self.current_date,
            "selected_idea": self.state.content_ideas[0] if self.state.content_ideas else {},
            "ideas": self.state.content_ideas[1:] if len(self.state.content_ideas) > 1 else [],
            "research_data": self.state.research_data,
            "synthesis_data": self.state.synthesis_data,
            "content_draft": self.state.content_draft
        }

        print(f"\nINFO: Inputs for crew: {inputs}")

        result = self.content_creation_crew.kickoff(inputs=inputs)
        print(f"\n====================DEBUG: response from content_creation_crew: {result.raw}")
        print(f"\n====================DEBUG: result.pydantic type: {type(result.pydantic)}")
        print(f"\n====================DEBUG: result.pydantic value: {result.pydantic}")

        # if hasattr(result.pydantic, 'title') and hasattr(result.pydantic, 'body'):
        #     # Lấy dữ liệu từ result.pydantic
        #     title = result.pydantic.title
        #     body = result.pydantic.body
        #     hashtags = ", ".join(result.pydantic.hashtags) if hasattr(result.pydantic, 'hashtags') else ""
        #     call_to_action = result.pydantic.call_to_action if hasattr(result.pydantic, 'call_to_action') else ""

        #     # Định dạng lại phản hồi
        #     response = (
        #         f"📢 **{title}**\n\n"
        #         f"{body}\n\n"
        #         f"🏷 **Hashtags:** {hashtags}\n"
        #         f"🔗 **{call_to_action}**"
        #     )
        # else:
        #     print("\n====================Không thể tổng hợp nội dung phản hồi")
        #     response = "Xin lỗi, tôi không thể tạo nội dung vào lúc này."
        if result.raw:
            response = result.raw
        else:
            response = "Xin lỗi, tôi không thể tạo nội dung vào lúc này."
        
        return response

def run_chat_flow():
    chat_flow = ContentChatFlow()
    chat_id = str(uuid.uuid4())
    message = "Tôi muốn tạo nội dung cho sản phẩm của tôi"
    history = [{"role": "assistant", "content": "Xin chào! Tôi có thể giúp gì cho bạn?"}, {"role": "user", "content": message}]
    content_info = ContentInfo(
        topic="Công nghệ",
        communication_goal="Quảng bá sản phẩm máy in brother ld2321",
        target_audience="Người dùng",
        brand_information="Brother",
        style_and_tone="Chuyên nghiệp, thân thiện, chính xác"
    )
    inputs={
                "id": chat_id,
                "message": message,
                "history": history,
                "content_info": content_info.model_dump()
            }
    result = chat_flow.kickoff(
        inputs=inputs
    )
    print(result) 
    
if __name__ == "__main__":
    run_chat_flow()
