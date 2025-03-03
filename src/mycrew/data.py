from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field  
# Step1: Define the ContentInfo model
class ContentInfo(BaseModel): #model thông tin nội dung do người dùng nhập vào
    topic: Optional[str] = Field(default=None, description="Chủ đề của nội dung")
    communication_goal: Optional[str] = Field(default=None, description="Mục tiêu truyền thông")
    target_audience: Optional[str] = Field(default=None, description="Đối tượng mục tiêu")
    brand_information: Optional[str] = Field(default=None, description="Thông tin thương hiệu")
    style_and_tone: Optional[str] = Field(default=None, description="Phong cách và giọng điệu")
    
# step 2: Define ContentIdea model
class ContentIdea(BaseModel): #model ý tưởng
    title: Optional[str] = Field(description="Tiêu đề ý tưởng")
    description: Optional[str] = Field(description="Mô tả ngắn gọn về ý tưởng")
    content_type: Optional[str] = Field(description="Loại nội dung (bài viết, hình ảnh, video, v.v.)")
    reason: Optional[str] = Field(description="Lý do ý tưởng phù hợp với mục tiêu và đối tượng")

# Create a wrapper class for the List[ContentIdea]
# để truyền vào task vì task không nhận List[ContentIdea]
class ContentIdeaList(BaseModel):
    ideas: List[ContentIdea] = Field(default_factory=list)
  # step 3: Define the OutputResearch model
 
class ContentResearch(BaseModel): #model tìm kiếm thông tin
    keywords: List[str] = Field(description="Các từ khóa liên quan")
    competitor_analysis: str = Field(description="Phân tích đối thủ cạnh tranh")
    trending_topics: List[str] = Field(description="Các chủ đề đang thịnh hành")
    statistics: str = Field(description="Các số liệu thống kê và dữ liệu liên quan")
    faq: List[str] = Field(description="Câu hỏi thường gặp từ đối tượng mục tiêu")
    insights: str = Field(description="Hiểu biết và phát hiện từ nghiên cứu")

# step 4: Define the OutputResearchSynthesis model
class ResearchSynthesis(BaseModel): #model tổng hợp thông tin
    key_insights: List[str] = Field(description="Các insight chính từ dữ liệu")
    unique_angle: str = Field(description="Góc nhìn độc đáo để tiếp cận chủ đề")
    key_elements: List[str] = Field(description="Các yếu tố quan trọng cần đưa vào nội dung")
    recommendations: List[str] = Field(description="Đề xuất cụ thể cho quá trình viết nội dung")

# step 5: Define the OutputContentWriting model
class ContentDraft(BaseModel): #model viết nội dung
    title: str = Field(description="Tiêu đề nội dung")
    body: str = Field(description="Nội dung chính")
    hashtags: List[str] = Field(description="Hashtags liên quan")
    call_to_action: str = Field(description="Kêu gọi hành động")
# step 6: Define the OutputContentFinal model
class ContentFinal(BaseModel): #model nội dung cuối cùng
    title: str = Field(description="Tiêu đề nội dung")
    body: str = Field(description="Nội dung chính")
    hashtags: List[str] = Field(description="Hashtags liên quan")
    call_to_action: str = Field(description="Kêu gọi hành động")
# step 6: Define the ChatState model
# Dùng trong app chatbot
class ChatState(BaseModel):
    # hội thoại
    id: str = ""  #input flow
    message: Optional[str] =  Field(default=None, description="Nội dung tin nhắn hiện tại") # input flow
    history: list[Dict[str, Any]] = Field(default=[], description="Lịch sử chat") # input flow
    # data trong flow
    content_info: Dict[str, Any] = Field(default_factory=dict)   #input flow
    content_ideas: List[Dict[str, Any]] = Field(default_factory=list, description="Ý tưởng nội dung") # idea output 
    research_data: Dict[str, Any] = Field(default_factory=dict, description="Dữ liệu nghiên cứu")
    synthesis_data: Dict[str, Any] = Field(default_factory=dict, description="Tổng hợp nghiên cứu")
    content_draft: List[Dict[str, Any]] = Field(default_factory=list, description="Bản nháp nội dung")

    # flag
    is_complete: bool = Field(default=False, description="Trạng thái hoàn thành")
    current_step: Optional[str] = Field(default="start", description="Bước hiện tại trong quy trình")

    # temp
    temp: Optional[str] = Field(default="", description="Dữ liệu tạm thời")