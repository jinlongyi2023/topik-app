import os
import streamlit as st
from openai import OpenAI
from supabase import create_client

# -------------------------
# 1. 连接 Supabase
# -------------------------
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")   # 从环境变量读取
SUPABASE_KEY = os.getenv("SUPABASE_KEY")   # 从环境变量读取

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 初始化 OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

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
                    st.rerun()  # 不提示“登录成功”，而是直接刷新进入作文批改界面
                else:
                    st.error("登录失败，请检查邮箱和密码。")
            except Exception as e:
                st.error(f"登录失败: {e}")


# -------------------------
# 4. 作文批改模块
# -------------------------
def essay_grading(essay):
    rules_text = get_scoring_rules()

    system_prompt = f"""
你是一位TOPIK写作官方考官，请严格按照以下评分规则批改作文。

【评分规则】
{rules_text}

【字数要求】
- 字数包含韩文字符、空格和标点符号。
- 不足600字：扣5分
- 不足500字：扣10分
- 不足400字：扣20分
- 不足300字：扣40分

【输出要求】
1. 计算字数并说明扣分情况
2. 按照评分规则逐项打分（每条规则写分数 + 理由）
3. 总分 = 所有小计 - 字数惩罚
4. 找拼写错误并改正
5. 中文点评（优点/问题/建议）
6. 给出韩语修改示例
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": essay}
        ],
        temperature=0.7
    )
    feedback = response.choices[0].message.content
    return feedback


# -------------------------
# 主逻辑：未登录 -> 登录界面；已登录 -> 批改界面
# -------------------------
if st.session_state["user"] is None:
    auth_form()
else:
    essay_grading()
