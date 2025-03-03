import gradio as gr
import uuid
from typing import List, Dict, Any, Optional
from main_flow import ContentChatFlow
from data import ContentInfo
            
# --- Giao diện Gradio ---
class ChatbotInterface:
    def __init__(self):
        self.chat_flows = {}
        self.chat_id = None
        self.default_response = [{"role": "assistant", "content": "Chào bạn, hãy nhập các trường thông tin và mình sẽ giúp tạo content cho bạn?"}]
    def chat(self, message: str, history: List[Dict[str, Any]],topic: str, goal: str, audience: str, brand: str, style: str) -> List[Dict[str, Any]]:
        """Process chat messages and maintain conversation history"""
        if not self.chat_id or not message:
            # Initialize new chat session
            self.chat_id = str(uuid.uuid4())
            self.chat_flows[self.chat_id] = ContentChatFlow() # tạo flow
            
        # Tạo ContentInfo từ input người dùng
        content_info = ContentInfo(
            topic=topic,
            communication_goal=goal,
            target_audience=audience,
            brand_information=brand,
            style_and_tone=style
        )
        # Nếu người dùng gửi tin nhắn, thêm tin nhắn của họ vào lịch sử trước khi xử lý
        new_history = history.copy()
        new_history.append({"role": "user", "content": message})

        # Xử lý tin nhắn của người dùng và nhận phản hồi từ chatbot
        bot_response = self._process_message(message, self.chat_id, new_history,content_info)
        print(f"[chat] Phản hồi của chatbot: {bot_response}")

        # Cập nhật lịch sử với phản hồi của chatbot
        new_history.append({"role": "assistant", "content": bot_response})

        # Trả về danh sách để hiển thị đúng thứ tự tin nhắn của người dùng và chatbot
        return [
            {"role": "assistant", "content": bot_response}  # Hiển thị phản hồi chatbot
        ]
        #return new_history
    # hàm xử lý tin nhắn và trả về phản hồi
    def _process_message(
        self, message: str, chat_id: str, history: List[Dict[str, Any]] = [], content_info: ContentInfo = None
    ) -> str:
        """Process a message through the chat flow"""
        chat_flow = self.chat_flows[chat_id]

        result = chat_flow.kickoff(
            inputs={
                "id": chat_id,
                "message": message,
                # "history": (
                #     "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)
                #     if history
                #     else ""
                # ),
                "history": history,
                "content_info": content_info.model_dump()
            }
        )
        return result
    

def create_content_chatbot() -> gr.Blocks:
    chatbot = ChatbotInterface()

    # Sử dụng gr.Blocks để bao bọc gr.ChatInterface và các ô input
    with gr.Blocks(title="Content Chatbot", theme=gr.themes.Ocean()) as demo:
        gr.Markdown("## 🤖 Content Creation Assistant")
        gr.Markdown("Hãy điền thông tin chi tiết để AI có thể tạo nội dung phù hợp nhất với nhu cầu của bạn!")

        # Sử dụng Group thay vì Box
        with gr.Group():
            # Tạo khoảng cách phía trên
            gr.Markdown("---")
            
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    topic_input = gr.Textbox(
                        label="📝 Chủ đề nội dung",
                        placeholder="VD: Máy in Brother LD2321 - Giải pháp in ấn cho doanh nghiệp vừa và nhỏ",
                        info="Mô tả ngắn gọn về chủ đề chính của nội dung",
                        lines=2,
                        max_lines=3,
                        container=True,
                        scale=1,
                        autofocus=True,
                        submit_btn="⏎"
                    )
                    goal_input = gr.Textbox(
                        label="🎯 Mục tiêu truyền thông",
                        placeholder="VD: Giới thiệu tính năng tiết kiệm mực...",
                        info="Mục tiêu cụ thể bạn muốn đạt được với nội dung này",
                        lines=2,
                        max_lines=3,
                        container=True,
                        scale=1,
                        submit_btn="⏎"
                    )

                with gr.Column(scale=1):
                    audience_input = gr.Textbox(
                        label="👥 Đối tượng mục tiêu",
                        placeholder="VD: Chủ doanh nghiệp vừa và nhỏ...",
                        info="Mô tả chi tiết về đối tượng khách hàng mục tiêu",
                        lines=2,
                        max_lines=3,
                        container=True,
                        scale=1,
                        submit_btn="⏎"
                    )
                    brand_input = gr.Textbox(
                        label="🏢 Thông tin thương hiệu",
                        placeholder="VD: Brother - Thương hiệu máy in Nhật Bản...",
                        info="Thông tin về thương hiệu và các giá trị cốt lõi",
                        lines=2,
                        max_lines=3,
                        container=True,
                        scale=1,
                        submit_btn="⏎"
                    )

            # Style input ở hàng riêng
            with gr.Row():
                style_input = gr.Textbox(
                    label="🎨 Phong cách và giọng điệu",
                    placeholder="VD: Chuyên nghiệp nhưng dễ hiểu...",
                    info="Xác định cách thức truyền đạt thông điệp phù hợp với đối tượng",
                    lines=2,
                    max_lines=2,
                    container=True,
                    scale=1,
                    submit_btn="⏎"
                )
            
            # Tạo khoảng cách phía dưới
            gr.Markdown("---")

        # Định nghĩa hàm chat với các tham số bổ sung
        def chat_with_inputs(message, history, topic, goal, audience, brand, style):
            return chatbot.chat(message, history, topic, goal, audience, brand, style)

        # Cấu hình Chatbot với các tính năng nâng cao
        chat_interface = gr.ChatInterface(
            fn=chat_with_inputs,  # Hàm xử lý logic chat
            additional_inputs=[    # Các trường input bổ sung
                topic_input,
                goal_input,
                audience_input,
                brand_input,
                style_input
            ],
            # Cấu hình giao diện chatbot
            chatbot=gr.Chatbot(
                label="💬 Content Assistant Chat",
                height=500,  # Chiều cao cố định cho khung chat
                
                # === Tính năng Copy ===
                show_copy_button=True,     # Cho phép copy từng tin nhắn riêng lẻ
                show_copy_all_button=True, # Thêm nút copy toàn bộ cuộc trò chuyện
                
                # === Cấu hình hiển thị ===
                type="messages",           # Định dạng tin nhắn kiểu OpenAI (role/content)
                value=chatbot.default_response,  # Tin nhắn chào mừng mặc định
                # avatar_images=(            # Ảnh đại diện cho user và bot
                #     "./assets/user.png",   # Đường dẫn đến ảnh user
                #     "./assets/bot.png"     # Đường dẫn đến ảnh bot
                # ),  
                # Hoặc dùng URL
                avatar_images=(
                    "https://img.freepik.com/free-vector/user-circles-set_78370-4704.jpg?t=st=1740734711~exp=1740738311~hmac=b57b205eb68e01a9da4fb109df45cdc3b8c173eaa3ede05ca5e61c55319c7089&w=1060",
                    "https://img.freepik.com/free-vector/cute-bot-say-users-hello-chatbot-greets-online-consultation_80328-195.jpg?t=st=1740734300~exp=1740737900~hmac=2a3760dc39d1bce2f2679ad821172639a19e3c13301faedcdbbb21eb3ddcb125&w=1060"
                ),
                
                # === Tùy chỉnh giao diện ===
                bubble_full_width=False,   # Tin nhắn co giãn theo nội dung
                layout="bubble",           # Giao diện dạng bong bóng chat hiện đại
                
                # === Hỗ trợ định dạng nội dung ===
                latex_delimiters=[         # Hỗ trợ hiển thị công thức toán học
                    {"left": "$$", "right": "$$", "display": True}
                ],
                line_breaks=True,          # Cho phép xuống dòng trong markdown
                render_markdown=True,       # Hỗ trợ định dạng markdown
                sanitize_html=True,        # Bảo mật - lọc các thẻ HTML nguy hiểm
                
                # === Tối ưu trải nghiệm người dùng ===
                placeholder="Hãy nhập yêu cầu của bạn để bắt đầu tạo nội dung...",  # Hướng dẫn khi chưa có tin nhắn
                autoscroll=True,           # Tự động cuộn đến tin nhắn mới nhất
                group_consecutive_messages=True,  # Gom nhóm tin nhắn liên tiếp từ cùng người gửi
            ),

            # Cấu hình ô nhập liệu
            textbox=gr.Textbox(
                placeholder="Nhập yêu cầu của bạn... (VD: Tạo nội dung bài đăng Facebook giới thiệu sản phẩm)",
                container=True,    # Bọc trong container để style đẹp hơn
                scale=7,           # Tỷ lệ chiều rộng so với các component khác
                show_label=False,  # Ẩn label vì không cần thiết
                lines=2,           # Số dòng tối thiểu
                max_lines=5,       # Số dòng tối đa khi mở rộng
                autofocus=False,    # Tự động focus khi load trang
                submit_btn=True,   # Hiện nút gửi và cho phép nhấn Enter
                autoscroll=True,   # Tự cuộn khi nội dung dài
                show_copy_button=True  # Cho phép copy nội dung đã nhập
            ),

            # === Cấu hình chung của interface ===
            submit_btn="🚀 Tạo nội dung",  # Label cho nút gửi
            title="Content Creation Assistant",  # Tiêu đề của ứng dụng
            description="Hệ thống AI hỗ trợ tạo nội dung thông minh",  # Mô tả ngắn
            theme="soft",          # Giao diện nhẹ nhàng, thân thiện
            autofocus=True,        # Tự động focus vào ô nhập liệu
            
            # === Tính năng ví dụ mẫu ===
            examples=[             # Các ví dụ với đầy đủ thông tin cho tất cả các trường
                [
                    "Tạo nội dung bài đăng Facebook",  # message
                    "Máy in Brother LD2321",           # topic
                    "Quảng bá sản phẩm máy in mới",   # goal
                    "Doanh nghiệp vừa và nhỏ",        # audience
                    "Brother - Thương hiệu máy in Nhật Bản", # brand
                    "Chuyên nghiệp và thân thiện"     # style
                ],
                [
                    "Tạo content cho LinkedIn",        # message
                    "Máy in Brother LD2321",          # topic
                    "Xây dựng thương hiệu chuyên nghiệp", # goal
                    "Giám đốc doanh nghiệp",         # audience
                    "Brother - 100 năm kinh nghiệm",  # brand
                    "Chuyên nghiệp và đáng tin cậy"  # style
                ]
            ],
            cache_examples=False,   # Tắt cache để tránh lỗi
            autoscroll=True,       # Tự động cuộn khi chọn ví dụ
        )

        # Thêm hướng dẫn sử dụng
        with gr.Accordion("ℹ️ Hướng dẫn sử dụng", open=False):
            gr.Markdown("""
            ### Cách sử dụng hiệu quả:
            1. **Điền đầy đủ thông tin** vào các trường bên trên càng chi tiết càng tốt
            2. **Gõ yêu cầu** của bạn vào ô chat (VD: "Tạo nội dung bài đăng Facebook")
            3. **Nhấn Enter hoặc nút Tạo nội dung** để bắt đầu
            4. Bạn có thể **yêu cầu chỉnh sửa** nếu muốn điều chỉnh nội dung
            
            ### Mẹo hay:
            - Sử dụng nút 'Thử lại' để tạo phiên bản khác của nội dung
            - Có thể copy nội dung bằng nút copy ở góc phải mỗi tin nhắn
            - Càng cung cấp nhiều thông tin, nội dung tạo ra càng phù hợp
            """)

    return demo

if __name__ == "__main__":
    chatbot = create_content_chatbot()
    chatbot.launch(share=True)
    
