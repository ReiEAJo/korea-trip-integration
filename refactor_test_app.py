import os

file_path = r"c:\Users\user\Downloads\ICB\korea trip project\korea-trip-data2\test\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip().startswith("st.set_page_config"):
        new_lines.append("# " + line)
    else:
        new_lines.append(line)

content = "".join(new_lines)
new_content = """def render_test_app():
""" + "\n".join("    " + line for line in content.split("\n")) + """

if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(page_title="한국 로컬 도시 분석", layout="wide")
    render_test_app()
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Refactored successfully")
