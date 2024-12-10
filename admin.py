import gradio as gr
import telegram
from telegram.ext import Application
from io import BytesIO

# Thông tin Telegram Bot (thay bằng token thực của bạn)
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Dữ liệu mockup user Telegram (giả lập 20 user)
all_users = [
    [f"User {i}", f"MSSV-{1000 + i}", f"Ngành {['IT', 'Biology', 'Math'][i % 3]}"] for i in range(1, 21)
]

# Hàm lọc người dùng theo mã số sinh viên hoặc ngành học
def filter_users(selected_id=None, selected_major=None):
    filtered_users = []
    for user in all_users:
        name, user_id, major = user
        if (selected_id and selected_id != user_id) or (selected_major and selected_major != major):
            continue
        filtered_users.append(user)
    return filtered_users or all_users

# Đồng bộ hóa slicer khi chọn trên bảng danh sách
def sync_slicer_on_user_select(selected_row):
    if not selected_row:
        return None, None
    selected_user = all_users[selected_row]
    return selected_user[1], selected_user[2]

# Đồng bộ hóa bảng khi chọn trên slicer
def sync_table_on_slicer_change(user_id, major):
    return filter_users(user_id, major)

# Hàm tải dữ liệu lên với điều kiện chọn bộ môn
def upload_data_to_telegram(subject, file):
    if not subject:
        return "Bạn phải chọn bộ môn trước khi tải lên dữ liệu!"
    if not file:
        return "Bạn phải tải lên tệp dữ liệu!"
    
    # Đọc file và thực hiện nạp dữ liệu vào hệ thống của bot
    content = file.read()
    bot.send_document(chat_id=TELEGRAM_BOT_TOKEN, document=BytesIO(content), filename=file.name)
    return f"Đã nạp dữ liệu cho bộ môn: {subject}"

# Dữ liệu mockup lịch sử trò chuyện (giả lập 20 user)
def fetch_chat_history(user_id, subject):
    # Lịch sử giả lập, có thêm bộ môn để phân loại
    history_mockup = {
        f"MSSV-{1000 + i}": {
            "IT": [f"IT Chat 1: Hi from User {i}", f"IT Chat 2: Any questions?"],
            "Biology": [f"Bio Chat 1: Hello from User {i}", f"Bio Chat 2: How can I help?"],
            "Math": [f"Math Chat 1: Welcome, User {i}", f"Math Chat 2: Let's solve problems!"]
        }
        for i in range(1, 21)
    }
    user_history = history_mockup.get(user_id, {})
    return user_history.get(subject, ["Không tìm thấy lịch sử trò chuyện với bộ môn này."])

# Tạo giao diện admin với 2 trang
with gr.Blocks() as admin_interface:
    gr.Markdown("# Giao diện Admin (Telegram)")
    
    # Tabs để chia trang
    with gr.Tab("Tải Tài Liệu"):
        gr.Markdown("## Trang Tải Tài Liệu")
        with gr.Row():
            subject_dropdown = gr.Dropdown(["IT", "Biology", "Mathematics"], label="Chọn bộ môn", interactive=True)
            file_uploader = gr.File(label="Tải lên tệp dữ liệu")
            upload_button = gr.Button("Nạp dữ liệu")
        upload_output = gr.Textbox(label="Trạng thái nạp dữ liệu", interactive=False)
        
        # Kết nối xử lý nạp dữ liệu
        upload_button.click(upload_data_to_telegram, inputs=[subject_dropdown, file_uploader], outputs=[upload_output])
    
    with gr.Tab("Kiểm Tra Lịch Sử"):
        gr.Markdown("## Trang Kiểm Tra Lịch Sử")
        with gr.Row():
            user_table = gr.Dataframe(all_users, headers=["Tên", "Mã số sinh viên", "Ngành học"], label="Danh sách user", interactive=True)
            with gr.Column():
                selected_user_id = gr.Dropdown(choices=[user[1] for user in all_users], label="Chọn mã số sinh viên")
                selected_major = gr.Dropdown(choices=["IT", "Biology", "Mathematics"], label="Chọn ngành học")
    
        chat_history = gr.Textbox(label="Lịch sử trò chuyện", interactive=False, lines=10)
        history_button = gr.Button("Xem lịch sử")
        
        # Kết nối xử lý kiểm tra lịch sử
        history_button.click(fetch_chat_history, inputs=[selected_user_id, selected_major], outputs=[chat_history])

    # Đồng bộ hóa bảng và slicer
    user_table.select(sync_slicer_on_user_select, inputs=None, outputs=[selected_user_id, selected_major])
    selected_user_id.change(sync_table_on_slicer_change, inputs=[selected_user_id, selected_major], outputs=user_table)
    selected_major.change(sync_table_on_slicer_change, inputs=[selected_user_id, selected_major], outputs=user_table)

# Khởi chạy giao diện
admin_interface.launch()
