# Import các thư viện cần thiết
import os
from dotenv import load_dotenv  # Để load biến môi trường từ file .env
from taipy.gui import Gui, State, notify, get_state_id, invoke_callback, Icon  # Import các component của Taipy GUI
from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin  # Base class cho agent executor
from crew import SocialContentCreatorCrew, register_output_handler  # Tích hợp CrewAI với Taipy
import time
import threading
from typing import List
from datetime import datetime
current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
# Load biến môi trường
load_dotenv()

# Khởi tạo danh sách users cho chat interface
# Mỗi user có tên và icon tương ứng
users: List[List[str | Icon]] = [
    ["Human", Icon("images/human_icon.png", "Human")],
    ["Researcher", Icon("images/researcher_icon.png", "Researcher")],
    ["Reporting Analyst", Icon("images/analyst_icon.png", "Analyst")],
    ["System", Icon("images/system_icon.png", "System")]
]

# Khởi tạo conversation với tin nhắn chào mừng
conversation = [
    ["1", "Chào bạn! Tôi là trợ lý ảo AI giúp tìm kiếm và viết blog, bạn cần tìm hiểu về topic nào?", "System"]
]

def on_init(state: State) -> None:
    """Khởi tạo conversation khi ứng dụng bắt đầu"""
    state.conversation = conversation.copy()

def update_conversation(state: State, sender: str, message: str):
    """
    Cập nhật conversation với tin nhắn mới
    Args:
        state: State hiện tại của GUI
        sender: Người gửi tin nhắn
        message: Nội dung tin nhắn
    """
    global conversation
    conversation += [[
        f"{len(conversation) + 1}",  # ID tin nhắn
        message,
        sender
    ]]
    state.conversation = conversation

def create_output_handler(state_id: str):
    """
    Tạo handler để xử lý output từ CrewAI
    Returns: Function handler nhận output và cập nhật conversation
    """
    return lambda output: invoke_callback(gui, state_id, lambda state: update_conversation(state, output.agent, output.raw))

# Flag kiểm tra trạng thái của crew
crew_started = False

def initiate_crew(state_id: str, message: str):
    """
    Khởi tạo và chạy CrewAI process
    Args:
        state_id: ID của state hiện tại
        message: Input message từ user
    """
    global crew_started
    
    try:
        # Đăng ký handler xử lý output
        register_output_handler(create_output_handler(state_id))
        
        # Khởi tạo và chạy crew với input từ user
        inputs = {"topic": message, "current_date": current_date}
        crew = SocialContentCreatorCrew().crew()
        result = crew.kickoff(inputs=inputs)
        
    except Exception as e:
        # Xử lý lỗi và hiển thị trong chat
        def show_error(state: State):
            update_conversation(state, "System", f"An error occurred: {e}")
        invoke_callback(gui, state_id, show_error)
    
    crew_started = False

# Biến global để lưu input từ user và state_id hiện tại
user_input = None
current_state_id = None

def custom_ask_human_input(self, final_answer: dict) -> str:
    """
    Custom function để nhận feedback từ user
    Thay thế hàm _ask_human_input mặc định của CrewAI
    """
    global user_input, current_state_id
    
    def update(state: State):
        update_conversation(state, "System", final_answer)
        human_feedback = "##PHẢN HỒI CỦA NGƯỜI DÙNG: Cung cấp phản hồi về Kết quả Cuối cùng và các hành động của Agent. Trả lời bằng 'looks good' (tốt) để chấp nhận hoặc cung cấp các yêu cầu cải tiến cụ thể. Bạn có thể cung cấp nhiều vòng phản hồi cho đến khi hài lòng."
        update_conversation(state, "System",  human_feedback)
    
    invoke_callback(gui, current_state_id, update)
    
    # Đợi user input
    while user_input is None:
        time.sleep(1)
    
    feedback = user_input
    user_input = None
    return feedback

# Override hàm _ask_human_input của CrewAI
CrewAgentExecutorMixin._ask_human_input = custom_ask_human_input

def send_message(state: State, var_name: str, payload: dict = None):
    """
    Xử lý việc gửi tin nhắn và khởi tạo CrewAI
    Args:
        state: State hiện tại
        var_name: Tên biến
        payload: Dữ liệu tin nhắn
    """
    global crew_started, user_input, current_state_id
    
    if payload:
        args = payload.get("args", [])
        message = args[2]
        sender = args[3]
        
        if not crew_started:
            # Bắt đầu CrewAI process
            current_state_id = get_state_id(state)
            update_conversation(state, sender, message)
            
            crew_started = True
            thread = threading.Thread(
                target=initiate_crew, 
                args=[current_state_id, message],
                daemon=True
            )
            thread.start()
            
        elif crew_started:
            # Xử lý feedback từ user trong quá trình CrewAI chạy
            user_input = message
            update_conversation(state, sender, message)

# Định nghĩa giao diện Taipy với component chat
page = """
<|{conversation}|chat|users={users}|on_action=send_message|sender_id=Human|show_sender=True|mode=markdown|>
"""

# Khởi tạo Taipy GUI
gui = Gui(page)

# Chạy ứng dụng
if __name__ == "__main__":
    gui.run(dark_mode=True, title="CrewAI Research Assistant")