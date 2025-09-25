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
                            "请用中文输出点评内容（例如：总体评价、主要错误、改进建议），"
                            "但学生作文中的修改示例和改正后的句子要用韩文。"
                        )
                    },
                    {"role": "user", "content": essay}
                ],
                temperature=0.7
            )

            feedback = response.choices[0].message.content

        # 显示结果
        st.subheader("批改结果（中文点评 + 韩文修改）：")
        st.write(feedback)
