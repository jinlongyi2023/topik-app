import streamlit as st

st.title("我的第一个 Streamlit Demo 🎉")
st.write("Hello, world! 这是我用 Streamlit 做的第一个 web 应用。")

name = st.text_input("请输入你的名字：")
if name:
    st.success(f"你好，{name}！欢迎来到我的 Demo～")
