import streamlit as st
from openai import OpenAI

# 使用 Streamlit Secrets 里的 API Key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("TOPIK 写作批改 Demo ✍️")

# 输入框
essay = st.text_area("请输入你的TOPIK作文：", height=300)

if st.button("批改我的作文"):
    if essay.strip() == "":
        st.warning("请输入作文后再提交！")
    else:
        with st.spinner("正在批改中，请稍候..."):
            # 调用 OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一位专业的TOPIK韩语写作老师。"
                            "请用 **中文** 给学生写详细点评（比如：总体评价、主要错误、写作建议），"
                            "但所有修改示例和改正后的句子要用 **韩文**。"
                        )
                    },
                    {"role": "user", "content": essay}
                ],
                temperature=0.7,
