import os
import streamlit as st
from openai import OpenAI
from supabase import create_client

# -------------------------
# 1. 连接 Supabase
# -------------------------
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase = create_client(url, key)

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
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
你是一位TOPIK写作考试的官方考官，请严格按照以下要求批改考生的大作文。

【评分标准】
1. 内容 (满分12分)
   - 是否与主题相关（0~4分）
   - 中心思想是否明确（0~4分）
   - 内容是否丰富（0~4分）

2. 结构 (满分12分)
   - 结构是否清晰（0~4分）
   - 中心思想是否组织良好（0~4分）
   - 是否使用恰当连接词（0~4分）

3. 表达 (满分26分)
   - 词汇使用是否丰富（0~9分）
   - 语法是否准确（0~9分）
   - 文体是否符合要求（0~8分）

【字数要求】
- 字数包含韩文字符、空格和标点符号。
- 不足600字：扣5分
- 不足500字：扣10分
- 不足400字：扣20分
- 不足300字：扣40分

【输出要求】
1. 计算字数（含空格和标点），并写明扣分情况。
2. 逐项打分：内容 / 结构 / 表达 → 每个细则都要写分数和理由。
3. 总分 = 三部分之和 - 字数惩罚分。
4. 找出拼写错误的单词，并给出正确写法。
5. 用中文给出点评（优点 + 主要问题 + 改进建议）。
6. 给出几句关键句的修改示例（用韩语改写）。

【输出格式示例】
字数：482字 → 少于500字，惩罚 -10分

内容 (共12分)：
- 与主题相关：3/4 → 紧扣主题，但论据不足
- 中心思想明确：2/4 → 主旨不够清晰
- 内容丰富：2/4 → 论据较少
小计：7/12

结构 (共12分)：
- 结构清晰：3/4
- 中心思想组织：3/4
- 连接词使用：2/4
小计：8/12

表达 (共26分)：
- 词汇丰富：6/9
- 语法准确：7/9 → 助词使用有误
- 文体符合：6/8
小计：19/26

总分：34/50 → 字数惩罚后 24/50

拼写错误：
- *학생들읃* → 正确：*학생들을*

中文点评：
优点：主题明确，段落较完整。  
问题：论据不足，语言错误较多。  
建议：加强连接词使用，丰富论据。

韩语修改示例：
- 잘못된 표현: "나는 학교 가다"  
  修改: "나는 학교에 갔다"
"""
            },
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
