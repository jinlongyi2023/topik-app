import streamlit as st
from openai import OpenAI
from supabase import create_client

# -------------------------
# 1. 连接 Supabase
# -------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 初始化 OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------
# 2. 初始化 session 状态
# -------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None  # 当前登录用户


# -------------------------
# 3. 注册 + 登录模块
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
                    st.success("登录成功！")
                else:
                    st.error("登录失败，请检查邮箱和密码。")
            except Exception as e:
                st.error(f"登录失败: {e}")


# -------------------------
# 4. 作文批改模块
# -------------------------
def essay_grading():
    st.title("TOPIK 写作批改 Demo ✍️")

    essay = st.text_area("请输入你的TOPIK作文：", height=300)

if st.button("批改我的作文"):
    if essay.strip() == "":
        st.warning("请输入作文后再提交！")
    else:
        with st.spinner("正在批改中，请稍候..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一名TOPIK写作官方评分老师。请严格按照以下评分标准进行：\n\n"
                            "【评分细则】\n"
                            "总分50分，由三部分组成：\n"
                            "1. 内容 (12分) - 是否与主题相关，中心思想清晰，内容丰富。\n"
                            "2. 结构 (12分) - 是否逻辑清晰，段落组织合理，衔接得当。\n"
                            "3. 语言使用 (26分) - 语法/词汇/拼写的准确性，句型多样性，表达是否自然。\n\n"
                            "【字数要求】\n"
                            "- 少于500字：不能给‘上’档分。\n"
                            "- 少于300字：不能给‘上’‘中’档分。\n"
                            "- 字数不足扣5分。\n\n"
                            "【输出要求】\n"
                            "1. 逐项打分：内容 / 结构 / 语言使用\n"
                            "2. 总分 = 三部分之和（考虑字数惩罚）\n"
                            "3. 中文点评（优点 + 主要问题 + 改进建议）\n"
                            "4. 给出几句关键的修改示例（用韩语改写）\n"
                        )
                    },
                    {"role": "user", "content": essay}
                ],
                temperature=0.7
            )

            feedback = response.choices[0].message.content

            st.subheader("批改结果（中文点评 + 韩文修改）：")
            st.write(feedback)


# -------------------------
# 主逻辑：未登录 -> 登录界面；已登录 -> 批改界面
# -------------------------
if st.session_state["user"] is None:
    auth_form()
else:
    essay_grading()
