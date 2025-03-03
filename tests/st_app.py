import streamlit as st
import os
from datetime import datetime
from crew import SocialContentCreatorCrew # Giả định class này được define ở file crew.py
from crewai import Process # Import Process từ crewai
from llm import togetherai_llm, gemini_llm # Giả định các LLM instances được define ở file llm.py
from utils import capture_output # Giả định context manager capture_output được define ở file utils.py
import asyncio # Thư viện để chạy các hàm async

st.set_page_config(page_title="Social Content Creator", layout="wide") # Thiết lập cấu hình trang Streamlit: tiêu đề và layout rộng
st.sidebar.header("LLM Configuration") # Tạo header "LLM Configuration" trong sidebar

llm_choice = st.sidebar.selectbox( # Tạo selectbox trong sidebar để chọn LLM
    "Choose LLM Model", # Label của selectbox
    ["TogetherAI (Llama-3.3-70B)", "Gemini-1.5-flash"] # Các option cho selectbox
)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1) # Slider trong sidebar để chọn temperature
top_p = st.sidebar.slider("Top P", 0.0, 1.0, 0.9, 0.1) # Slider trong sidebar để chọn top_p
timeout = st.sidebar.slider("Timeout (seconds)", 30, 300, 120, 10) # Slider trong sidebar để chọn timeout

if llm_choice == "TogetherAI (Llama-3.3-70B)": # Nếu người dùng chọn TogetherAI
    togetherai_llm.temperature = temperature # Cập nhật thuộc tính temperature của đối tượng togetherai_llm
    togetherai_llm.top_p = top_p # Cập nhật thuộc tính top_p của đối tượng togetherai_llm
    togetherai_llm.timeout = timeout # Cập nhật thuộc tính timeout của đối tượng togetherai_llm
else: # Nếu người dùng chọn Gemini-1.5-flash (else if vì chỉ có 2 lựa chọn)
    gemini_llm.temperature = temperature # Cập nhật thuộc tính temperature của đối tượng gemini_llm
    gemini_llm.top_p = top_p # Cập nhật thuộc tính top_p của đối tượng gemini_llm
    gemini_llm.timeout = timeout # Cập nhật thuộc tính timeout của đối tượng gemini_llm

with st.sidebar.expander("📖 Instructions", expanded=False): # Tạo expander "📖 Instructions" trong sidebar, mặc định đóng
    st.markdown(""" # Nội dung markdown bên trong expander, hiển thị hướng dẫn sử dụng
    **Flow:**
    1. Configure LLM parameters.
    2. Enter your topic.
    3. Click **Generate Content**.
    4. Xem log hoạt động của agent trong phần **Agent Logs**.
    5. Khi agent yêu cầu feedback (human_input đã được cài sẵn trong task), hãy nhập phản hồi vào ô **Human Feedback** bên dưới và nhấn Submit.
    6. Kết quả cuối cùng xuất hiện trong mục **Final Content** (có thể chỉnh sửa).
    """)

st.title("🤖 Social Content Creator") # Tiêu đề chính của ứng dụng Streamlit
topic = st.text_input("Enter your topic:", "top các địa điểm đẹp Hải Phòng") # Ô nhập text để người dùng nhập topic, mặc định là "top các địa điểm đẹp Hải Phòng"
main_container = st.container() # Tạo container chính để chứa các thành phần UI bên dưới tiêu đề và ô nhập topic



# Async function to run content generation
async def run_generation():
    """
    Hàm không đồng bộ để chạy quá trình tạo nội dung bằng CrewAI và hiển thị logs.
    Phiên bản tối giản, chỉ tập trung vào hiển thị Agent Logs.
    """
    current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") # Tạo timestamp (không dùng trong phiên bản tối giản này nhưng vẫn giữ lại)
    with main_container: # Sử dụng container chính
        status_container = st.empty() # Placeholder container để hiển thị status (không dùng nhiều trong phiên bản tối giản này)
        with st.expander("Agent Logs", expanded=True): # Expander để chứa logs, mặc định mở
            log_container = st.container(height=400, border=True) # Container bên trong expander để hiển thị logs

        try: # Bắt lỗi
            with status_container: # Sử dụng status container (không dùng nhiều trong phiên bản tối giản này)
                with st.status("🤖 Agents are working...", expanded=True) as status: # Hiển thị status message (không dùng nhiều trong phiên bản tối giản này)
                    with capture_output(log_container): # Capture output (stdout) và hiển thị trong log_container
                        crew_instance = SocialContentCreatorCrew() # Khởi tạo Crew instance (từ file crew.py hoặc mock class)
                        # KHÔNG CÓ xử lý human input trong phiên bản tối giản này

                        result = crew_instance.crew().kickoff( # Gọi kickoff để chạy CrewAI
                            inputs={
                                'topic': topic, # Topic từ input của user
                                'current_date': current_date # Current date 
                            }
                        )
                        status.update(label="✅ Content generated successfully!", state="complete") # Cập nhật status (không dùng nhiều trong phiên bản tối giản này)

            st.markdown("### 📝 Final Content:") # Markdown header cho final content
            st.write(result) # Hiển thị kết quả cuối cùng (text đơn giản)

        except Exception as e: # Bắt lỗi
            status_container.error(f"❌ Error: {str(e)}") # Hiển thị error (không dùng nhiều trong phiên bản tối giản này)
            st.error(f"Detailed error: {str(e)}") # Hiển thị detailed error

# Button Generate Content now calls the async function
if st.button("Generate Content", type="primary", use_container_width=True): # Button "Generate Content"
    asyncio.run(run_generation()) # Chạy hàm run_generation khi button click