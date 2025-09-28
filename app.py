import os
import streamlit as st
from openai import OpenAI
from supabase import create_client

# -------------------
# 1. 连接 Supabase
# -------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------
# 2. 初始化 OpenAI
# -------------------
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# -------------------
# 3. 批改函数
# -------------------
def essay_grading(essay: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一名TOPIK写作官方评分老师，请严格按照以下标准进行打分：\n\n"
                    "【评分细则】\n"
                    "1. 内容（12分）：是否与主题相关、中心思想清晰、内容丰富。\n"
                    "2. 结构（12分）：文章结构是否清晰，逻辑是否合理，是否使用恰当连接词。\n"
                    "3. 表达（26分）：词汇是否丰富、语法是否准确、文体是否自然。\n\n"
                    "【字数要求】\n"
                    "- 少于600字：扣5分。\n"
                    "- 少于500字：扣10分。\n"
                    "- 少于400字：扣20分。\n"
                    "- 少于300字：扣40分。\n"
                    "（字数包含空格、韩文字、标点符号）\n\n"
                    "【输出要求】\n"
                    "1. 统计字数（含空格和标点）。\n"
                    "2. 各项评分：内容 / 结构 / 表达。\n"
                    "3. 总分（考虑字数惩罚）。\n"
                    "4. 找出拼写错误并改正。\n"
                    "5. 中文点评（优点 + 问题 + 改进建议）。\n"
                    "6. 给出几个关键句的修改示例（用韩语改写）。\n"
                )
            },
            {"role": "user", "content": essay}
        ],
        temperature=0.7
    )

    feedback = response.choices[0].message.content
    return feedback


# -------------------
# 4. Streamlit 界面
# -------------------
st.title("TOPIK 大作文批改系统 ✍️")

essay_text = st.text_area("请输入你的作文：", height=300)

if st.button("批改作文"):
    if essay_text.strip():
        st.info("正在批改，请稍候...")
        feedback = essay_grading(essay_text)

        st.subheader("批改结果")
        st.write(feedback)

        # 存储到 Supabase
        supabase.table("compositions").insert({
            "content": essay_text,
            "feedback": feedback
        }).execute()

    else:
        st.warning("请输入作文后再点击批改按钮！")


# -------------------------
# 5. 注册 + 登录模块
# -------------------------
def auth_form():
    st.subheader("请先登录 / 注册")

    email = st.text_input("邮箱")
    password = st.text_input("密码", type="password")

    col1, col2 = st.columns(2)

    # 注册
    with col1:
        if st.button("注册"):
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                if res.user:
                    # 注册成功后自动登录
                    login_res = supabase.auth.sign_in_with_password(
                        {"email": email, "password": password}
                    )
                    st.session_state["user"] = login_res.user
                    st.success("注册并已自动登录成功！")
                else:
                    st.warning("注册失败，请检查邮箱是否已存在。")
            except Exception as e:
                st.error(f"注册失败: {e}")

    # 登录
    with col2:
        if st.button("登录"):
            try:
                res = supabase.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
                if res.user:
                    st.session_state["user"] = res.user
                    st.rerun()  # 不提示“登录成功”，而是直接刷新进入作文批改界面
                else:
                    st.error("登录失败，请检查邮箱和密码。")
            except Exception as e:
                st.error(f"登录失败: {e}")
