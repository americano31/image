import streamlit as st
import requests
import os
import zipfile
import shutil
from io import BytesIO

# 다운로드 디렉토리
DOWNLOAD_DIR = "images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 임시 선택 이미지 저장소
selected_images = []

# 이미지 정보 저장 리스트 (url, source, type)
image_data = [
    {"url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885_960_720.jpg", "source": "Pixabay", "type": "자연"},
    {"url": "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg", "source": "Pexels", "type": "건축"},
    {"url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb", "source": "Unsplash", "type": "풍경"},
    # 여기에 API 결과를 연결하여 동적으로 채울 수 있음
]

st.title("🔍 이미지 검색 결과 - 선택 다운로드")
st.write("이미지를 선택한 후 ZIP으로 다운로드하세요.")

cols = st.columns(5)

for idx, data in enumerate(image_data):
    col = cols[idx % 5]
    with col:
        st.image(data["url"], use_column_width=True)
        st.caption(f"출처: {data['source']} / 유형: {data['type']}")
        if st.checkbox("선택", key=data["url"]):
            selected_images.append(data)

if selected_images:
    if st.button("선택한 이미지 ZIP 다운로드"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            source_log = ""
            for idx, item in enumerate(selected_images):
                response = requests.get(item["url"])
                ext = item["url"].split(".")[-1].split("?")[0]
                filename = f"image_{idx+1}.{ext}"
                zipf.writestr(filename, response.content)
                source_log += f"{filename}, {item['source']}, {item['url']}, {item['type']}\n"
            # 출처 로그 추가
            zipf.writestr("출처_정보.csv", source_log)

        st.download_button(
            label="📦 ZIP 파일 다운로드",
            data=zip_buffer.getvalue(),
            file_name="selected_images.zip",
            mime="application/zip"
        )
else:
    st.info("이미지를 하나 이상 선택해주세요.")
