import streamlit as st
import requests
import os
import zipfile
import re
from io import BytesIO
from PIL import Image
from urllib.parse import quote

# 🔐 API KEY (secrets.toml에서 불러오기)
UNSPLASH_KEY = st.secrets["UNSPLASH_KEY"]
PIXABAY_KEY = st.secrets["PIXABAY_KEY"]
PEXELS_KEY = st.secrets["PEXELS_KEY"]

DOWNLOAD_DIR = "images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ✅ 세션 상태 초기화
if "selected_images" not in st.session_state:
    st.session_state.selected_images = {}
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False
if "all_checked" not in st.session_state:
    st.session_state.all_checked = False

# 📥 이미지 다운로드

def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except:
        pass
    return False

# 🔍 Unsplash 검색

def search_unsplash(keyword, count):
    st.markdown("### 📷 Unsplash")
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    url = f"https://api.unsplash.com/search/photos?query={quote(keyword)}&per_page={count}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json().get("results", [])
        cols = st.columns(5)
        for idx, photo in enumerate(results):
            thumb_url = photo["urls"]["small"]
            img_url = photo["urls"]["raw"]
            origin_url = photo["links"]["html"]
            author = photo["user"].get("name", "unknown")
            checkbox_id = f"unsplash_{idx}"
            with cols[idx % 5]:
                st.image(thumb_url, use_container_width=True)
                checked = st.checkbox(f"Unsplash #{idx+1}", key=checkbox_id, value=st.session_state.all_checked)
                if checked:
                    st.session_state.selected_images[checkbox_id] = (img_url, origin_url, author)
                elif checkbox_id in st.session_state.selected_images:
                    del st.session_state.selected_images[checkbox_id]
    else:
        st.warning("Unsplash에서 이미지를 가져올 수 없습니다.")

# 🔍 Pixabay 검색

def search_pixabay(keyword, count):
    st.markdown("### 📸 Pixabay")
    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={quote(keyword)}&per_page={count}&image_type=photo"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("hits", [])
        cols = st.columns(5)
        for idx, item in enumerate(results):
            img_url = item["webformatURL"]
            page_url = item["pageURL"]
            author = item.get("user", "unknown")
            checkbox_id = f"pixabay_{idx}"
            with cols[idx % 5]:
                st.image(img_url, use_container_width=True)
                checked = st.checkbox(f"Pixabay #{idx+1}", key=checkbox_id, value=st.session_state.all_checked)
                if checked:
                    st.session_state.selected_images[checkbox_id] = (img_url, page_url, author)
                elif checkbox_id in st.session_state.selected_images:
                    del st.session_state.selected_images[checkbox_id]
    else:
        st.warning("Pixabay API 오류")

# 🔍 Pexels 검색

def search_pexels(keyword, count):
    st.markdown("### 📷 Pexels")
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/v1/search?query={quote(keyword)}&per_page={count}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json().get("photos", [])
        cols = st.columns(5)
        for idx, photo in enumerate(results):
            img_url = photo["src"]["medium"]
            origin_url = photo["url"]
            author = photo["photographer"]
            checkbox_id = f"pexels_{idx}"
            with cols[idx % 5]:
                st.image(img_url, use_container_width=True)
                checked = st.checkbox(f"Pexels #{idx+1}", key=checkbox_id, value=st.session_state.all_checked)
                if checked:
                    st.session_state.selected_images[checkbox_id] = (img_url, origin_url, author)
                elif checkbox_id in st.session_state.selected_images:
                    del st.session_state.selected_images[checkbox_id]
    else:
        st.warning("Pexels API 오류")

# 🔃 ZIP 파일 생성

def create_zip(images, zip_name="selected_images.zip"):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, (url, origin_link, author) in enumerate(images):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    ext = "jpg"
                    img_data = response.content
                    safe_author = re.sub(r'\W+', '_', author) if author else 'unknown'
                    filename = f"image_{idx+1}_by_{safe_author}.{ext}"
                    zipf.writestr(filename, img_data)
                    zipf.writestr(f"image_{idx+1}.txt", f"Source: {origin_link}")
            except:
                continue
    return zip_buffer

# ▶ Streamlit 앱 UI

st.title("🔍 이미지 검색 & 선택 다운로드")

keyword = st.text_input("검색어를 입력하세요 (예: 제주오름)", value="비행기")
count = st.slider("API별 가져올 이미지 수", 1, 20, 10)

if st.button("🔎 이미지 검색"):
    st.session_state.search_triggered = True

if st.session_state.search_triggered:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 전체 선택"):
            st.session_state.all_checked = True
            st.rerun()
    with col2:
        if st.button("❌ 전체 선택 해제"):
            st.session_state.all_checked = False
            st.session_state.selected_images.clear()
            st.rerun()

    with st.spinner("이미지를 검색 중입니다..."):
        search_unsplash(keyword, count)
        search_pixabay(keyword, count)
        search_pexels(keyword, count)

if st.session_state.selected_images:
    st.markdown("---")
    st.success(f"선택한 이미지 수: {len(st.session_state.selected_images)}")
    download_mode = st.radio("다운로드 방식 선택", ["ZIP으로 저장", "이미지별 다운로드"])

    if download_mode == "ZIP으로 저장":
        if st.button("📁 ZIP 저장"):
            zip_file = create_zip(list(st.session_state.selected_images.values()))
            st.download_button("💾 ZIP 파일 다운로드", zip_file.getvalue(), file_name="selected_images.zip", mime="application/zip")

    elif download_mode == "이미지별 다운로드":
        for idx, (url, origin_link, author) in enumerate(st.session_state.selected_images.values()):
            cols = st.columns([4, 1, 2])
            with cols[0]:
                st.image(url, use_column_width=True)
            with cols[1]:
                st.download_button(
                    label="💾 이미지 다운로드",
                    data=requests.get(url).content,
                    file_name=f"image_{idx+1}_by_{author}.jpg",
                    mime="image/jpeg"
                )
            with cols[2]:
                st.markdown(f"[🔗 출처 바로가기]({origin_link})")
else:
    st.info("이미지를 하나 이상 선택해주세요.")
