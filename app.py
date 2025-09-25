import streamlit as st
from openai import OpenAI
from supabase import create_client

# -------------------------
# 1. 连接 Supabase
# -------------------------
url = st.secrets["https://ruajtxpodbcvjkxzrgpy.supabase.co"]   # 放在 Streamlit Secrets 里
key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1YWp0eHBvZGJjdmpreHpyZ3B5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4MDczNjksImV4cCI6MjA3NDM4MzM2OX0.5uuzSP2mENwTXKAGW_IGGj7hnID0YJ7W289Oyw5eOyY"]   # anon public key
supabase = create_client(url, key)

# -------------------------
# 2. 初始化状态
# -------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None   # 当前登录用户


# -------------------------
# 3. 注册 + 登录模块
# -------------------------
def auth_form():
    st.subheader("请先登录 / 注册")

    email = st.text_input("邮箱")
    password = st.text_input("密码", type="password")

    # 注册（注册成功后自动登录）
    if st.button("注册"):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            login_res = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if login_res.user:
                st.session_state["user"] = login_res.user
                st.success("注册并已自动登录成功！")
        except Exception as e:
            st.error(f"注册失败: {e}")

    # 登录
    if st.button("登录"):
        try:
            res = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if res.user:
                st.session_state["user"] = res.user
                st.success("登录成功！")
        except Exception as e:
            st.error(f"登录失败: {e}")


# -------------------------
# 4. 批改作文模块
# -------------------------
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
                            "请根据以下要求批改学生的作文：\n\n"
                            "1. 输出语言：点评部分必须用中文；句子修改示例必须用韩语。\n"
                            "2. 批改内容结构：\n"
                            "   - 【总体评价】：给出整体印象（主题是否清晰，逻辑是否连贯）。\n"
                            "   - 【主要错误】：指出作文中的主要错误（语法、用词、表达问题）。\n"
                            "   - 【修改示例】：列出原句（韩语）和修改后的句子（韩语），保持1对1对照。\n"
                            "   - 【改进建议】：给出提升建议（比如词汇多样性、句式复杂度）。\n"
                            "3. 给出分数：按照 TOPIK 写作评分标准，从以下3个维度分别打分（满分30）：\n"
                            "   - 内容 (Content)\n"
                            "   - 结构 (Structure)\n"
                            "   - 表达 (Expression)\n"
                            "   最后给出总分 (满分90)。\n\n"
                            "请严格按照上述格式输出，方便学生理解和改进。"
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
