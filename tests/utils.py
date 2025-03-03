# import agentops

# agentops.init(
#     api_key='6907fe8e-b6ae-452c-848e-2955ba4340a8',
#     default_tags=['crewai']
# )


# def create_content_chatbot() -> gr.Blocks:
#     chatbot = ChatbotInterface()
#     demo = gr.ChatInterface(
#         chatbot.chat,
#         chatbot=gr.Chatbot(
#             label="Lead Qualification Chat",
#             height=600,
#             show_copy_button=True,
#             type="messages",  # Sử dụng định dạng messages
#             value=chatbot.default_response,
#         ),
#         textbox=gr.Textbox(
#             placeholder="Nhập tin nhắn của bạn...",
#             container=True,
#             scale=7,
#             show_label=False,
#         ),
#         submit_btn="Send",
#         title="content Chatbot",
#         description="description",
#         examples=[
#             "Hi, tôi muốn làm content về sức khỏe",
#             "Hi, tôi muốn làm content về công nghệ",
#         ],
#         type="messages",  # Đảm bảo ChatInterface sử dụng định dạng messages
#         autofocus=True,
#     )
#     return demo

#     def _process_message1(
#     self, message: str, chat_id: str, history: List[Dict[str, Any]] = [],content_info: ContentInfo = None
# ) -> str:
#         """Process a message through the chat flow (Test mode)"""
#         print(f"[_process_message] Xử lý tin nhắn: {message}")
#         print(f"[_process_message] Lịch sử hội thoại:\n{history}")

#         # Trả về phản hồi cố định để kiểm tra giao diện
#         result = "Test response from chatbot"
#         print(f"[_process_message] Phản hồi chatbot (giả lập): {result}")
#         print(f"[_process_message] Content Info: {content_info}")
#         print(f"[_process_message] Chat ID: {chat_id}")

#         return result

# flowchart TD
#     A[Start Flow] --> B[Generate Content Ideas]
#     B --> C[User Selects Idea]
#     C --> D[Conduct Research]
#     D --> E[Synthesize Research]
#     E --> F[Write Content]
#     F --> G[Review Content]
#     G --> H{User Approves?}
#     H -->|Yes| I[Finalize Content]
#     H -->|No| J[Revise Content]
#     J --> G
#     I --> K[Complete]
    
#     subgraph "Research & Synthesis"
#         D --> |"Keywords\nTrends\nCompetitors\nStatistics\nFAQ"| D1[Raw Research Data]
#         D1 --> E
#         E --> |"Key Insights\nUnique Angle\nKey Elements\nRecommendations"| E1[Synthesized Research]
#         E1 --> F
#     end

    # def model_dump(self, *args, **kwargs):
    #     # Chuyển đổi content_info thành dictionary trước khi dump
    #     data = super().model_dump(*args, **kwargs)
    #     if isinstance(self.content_info, ContentInfo):
    #         data["content_info"] = self.content_info.model_dump()
    #     return data

    # @classmethod
    # def from_dict(cls, data: Dict[str, Any]) -> "ChatState":
    #     # Khôi phục lại content_info thành một object ContentInfo khi load
    #     if "content_info" in data and isinstance(data["content_info"], dict):
    #         data["content_info"] = ContentInfo(**data["content_info"])
    #     return cls(**data)