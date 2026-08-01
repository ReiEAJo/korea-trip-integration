import os
import re
import base64
import markdown

with open('total_integrated_eda.md', 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert markdown to html
html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

# Replace img tags with base64 data URIs
def replace_img(match):
    src = match.group(1)
    if os.path.exists(src):
        ext = os.path.splitext(src)[1][1:]
        if ext.lower() == 'jpg':
            ext = 'jpeg'
        with open(src, 'rb') as img_f:
            b64_data = base64.b64encode(img_f.read()).decode('utf-8')
        return f'src="data:image/{ext};base64,{b64_data}"'
    return match.group(0)

html = re.sub(r'src="(images/[^"]+)"', replace_img, html)

full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>통합 한국 관광 데이터 탐색적 분석 (EDA) 보고서</title>
<style>
body {{ font-family: "Malgun Gothic", sans-serif; line-height: 1.6; padding: 20px; max-width: 1000px; margin: 0 auto; }}
img {{ max-width: 100%; height: auto; display: block; margin: 20px auto; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background-color: #f2f2f2; }}
h1, h2, h3 {{ color: #333; }}
blockquote {{ border-left: 4px solid #ddd; padding-left: 10px; color: #555; }}
pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
code {{ font-family: Consolas, monospace; background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; }}
</style>
</head>
<body>
{html}
</body>
</html>"""

with open('korea_trip_eda_report.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Successfully generated HTML")
