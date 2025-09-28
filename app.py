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
    return response.choices[0].message.content


# -------------------
# 4. 注册 / 登录系统
# -------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

st.sidebar.title("用户中心")

if st.session_state["user"] is None:
    option = st.sidebar.radio("请选择操作：", ["登录", "注册"])

    if option == "登录":
        email = st.sidebar.text_input("邮箱")
        password = st.sidebar.text_input("密码", type="password")
        if st.sidebar.button("登录"):
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                st.session_state["user"] = res.user
                st.success("登录成功！")
            else:
                st.error("登录失败，请检查邮箱和密码。")

    elif option == "注册":
        email = st.sidebar.text_input("邮箱")
        password = st.sidebar.text_input("密码", type="password")
        if st.sidebar.button("注册"):
            res = supabase.auth.sign_up({"email": email, "password": password})
            if res.user:
                st.success("注册成功，请登录。")
            else:
                st.error("注册失败。")

else:
    st.sidebar.write(f"欢迎回来, {st.session_state['user'].email}")
    if st.sidebar.button("退出登录"):
        st.session_state["user"] = None


# -------------------
# 5. 主页面：作文批改
# -------------------
if st.session_state["user"]:
    st.title("TOPIK 大作文批改系统 ✍️")

    essay_text = st.text_area("请输入你的作文：", height=300)

    if st.button("批改作文"):
        if essay_text.strip():
            st.info("正在批改，请稍候...")
            feedback = essay_grading(essay_text)

            st.subheader("批改结果")
            st.markdown(feedback, unsafe_allow_html=True)

            # 存储到 Supabase
            supabase.table("compositions").insert({
                "user_id": st.session_state["user"].id,
                "content": essay_text,
                "feedback": feedback
            }).execute()

        else:
            st.warning("请输入作文后再点击批改按钮！")

    # -------------------
    # 6. 历史记录
    # -------------------
    st.subheader("历史批改记录")
    records = supabase.table("compositions").select("*").eq("user_id", st.session_state["user"].id).order("created_at", desc=True).execute()
    for r in records.data:
        with st.expander(f"作文 ID: {r['id']} | 批改时间: {r['created_at']}"):
            st.write("原文：")
            st.write(r["content"])
            st.write("批改结果：")
            st.write(r["feedback"])
