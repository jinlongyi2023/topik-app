import streamlit as st
from openai import OpenAI

# ---------------------------
# 1. 设置 OpenAI API Key
# ---------------------------
# 你需要在 Streamlit Cloud 里设置环境变量 OPENAI_API_KEY
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("TOPIK 写作批改 Demo ✍️")

# ---------------------------
# 2. 输入框
# ---------------------------
essay = st.text_area("请输入你的TOPIK作文：", height=300)

if st.button("批改我的作文"):
    if essay.strip() == "":
        st.warning("请输入作文后再提交！")
    else:
        with st.spinner("正在批改中，请稍候..."):
            # ---------------------------
            # 3. 调用 ChatGPT API
            # ---------------------------
            response = client.chat.completions.create(
                model="gpt-4o-mini",   # 你也可以用 gpt-4o 或 gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": "你是一位专业的TOPIK韩语写作老师，请帮学生修改作文，指出错误并给出改进建议。"},
                    {"role": "user", "content": essay}
                ],
                temperature=0.7,
            )
            feedback = response.choices[0].message.content

        # ---------------------------
        # 4. 显示结果
        # ---------------------------
        st.subheader("批改结果：")
        st.write(feedback)
