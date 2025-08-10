import streamlit as st
from qa_system import InventoryQASystem
import os

st.set_page_config(page_title="库存智能问答", page_icon="📊", layout="centered")
st.title("📊 库存智能问答系统")
st.caption("支持多轮对话，自动生成图表 | Powered by LLM + pandas + matplotlib")

# 初始化问答系统（只初始化一次）
if 'qa_system' not in st.session_state:
    st.session_state.qa_system = InventoryQASystem()

# 聊天历史
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # [(user, ai, [charts])]

# 用户输入
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("请输入您的问题：", "", key="user_input")
    submit = st.form_submit_button("发送")

if submit and user_input.strip():
    # 处理问题
    qa = st.session_state.qa_system
    ai_reply, charts = qa.analyze_data(user_input)
    st.session_state.chat_history.append((user_input, ai_reply, charts))

# 展示历史对话
for idx, (user, ai, charts) in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.markdown(f"**你：** {user}")
    with st.chat_message("assistant"):
        st.markdown(f"**AI：** {ai}")
        # 展示图表
        if charts:
            for chart in charts:
                if os.path.exists(chart['path']):
                    st.image(chart['path'], caption=chart['description'], use_column_width=True)

# 底部说明
st.markdown("---")
st.caption("© 2024 库存智能问答 | 简洁Web界面 | 支持多轮对话与图表展示") 