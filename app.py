import streamlit as st
from openai import OpenAI
from supabase import create_client

url = "https://ruajtxpodbcvjkxzrgpy.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1YWp0eHBvZGJjdmpreHpyZ3B5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MDczNjksImV4cCI6MjA3NDM4MzM2OX0.5uuzSP2mENwTXKAGW_IGGj7hnID0YJ7W289Oyw5eOyY"
supabase = create_client(url, key)

# 用户输入邮箱和密码
email = st.text_input("邮箱")
password = st.text_input("密码", type="password")

if st.button("注册"):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        # 注册后直接登录
        login_res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.success("注册并已自动登录成功！")
        st.json(login_res)
    except Exception as e:
        st.error(f"注册失败: {e}")

# 注册
if st.button("注册"):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.success("注册成功！")
        st.json(res)   # 打印结果看看
    except Exception as e:
        st.error(f"注册失败: {e}")

# 登录
if st.button("登录"):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.success("登录成功！")
        st.json(res)   # 打印结果看看
    except Exception as e:
        st.error(f"登录失败: {e}")

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
