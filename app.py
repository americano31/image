import streamlit as st
import requests
import os
import zipfile
from io import BytesIO
from PIL import Image
from urllib.parse import quote

# 🔑 API KEY
UNSPLASH_KEY = "j5lyiOKj0bj6iMFPgvCnO0cCB_eWEyx5NsXZr3VRR94"
PIXABAY_KEY = "51462455-6f4af1014e035b145b2e7731b"
PEXELS_KEY = "kd1frTIFwfExQIR5DIGn1eKJ7gEGUIbbWDKSmi3sLjGhv9nDVP0Qmnnh"

DOWNLOAD_DIR = "images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
    selected = []
    if response.status_code == 200:
        results = response.json().get("results", [])
        cols = st.columns(5)
        for idx, photo in enumerate(results):
            img_url = photo["urls"]["small"]
            download_url = photo["links"]["html"]
            with cols[idx % 5]:
                st.image(img_url, use_container_width=True)
                if st.checkbox(f"Unsplash #{idx+1}", key=f"unsplash_{idx}"):
                    selected.append((img_url, download_url))
    else:
        st.warning("Unsplash에서 이미지를 가져올 수 없습니다.")
    return selected

# 🔍 Pixabay 검색
def search_pixabay(keyword, count):
    st.markdown("### 📸 Pixabay")
    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={quote(keyword)}&per_page={count}&image_type=photo"
    response = requests.get(url)
    selected = []
    if response.status_code == 200:
        results = response.json().get("hits", [])
        if not results:
            st.warning("Pixabay에서 이미지를 찾을 수 없습니다.")
        cols = st.columns(5)
        for idx, item in enumerate(results):
            img_url = item["webformatURL"]
            page_url = item["pageURL"]
            with cols[idx % 5]:
                st.image(img_url, use_container_width=True)
                if st.checkbox(f"Pixabay #{idx+1}", key=f"pixabay_{idx}"):
                    selected.append((img_url, page_url))
    else:
        st.warning("Pixabay API 오류")
    return selected

# 🔍 Pexels 검색
def search_pexels(keyword, count):
    st.markdown("### 📷 Pexels")
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/v1/search?query={quote(keyword)}&per_page={count}"
    response = requests.get(url, headers=headers)
    selected = []
    if response.status_code == 200:
        results = response.json().get("photos", [])
        if not results:
            st.warning("Pexels에서 이미지를 찾을 수 없습니다.")
        cols = st.columns(5)
        for idx, photo in enumerate(results):
            img_url = photo["src"]["medium"]
            photo_url = photo["url"]
            with cols[idx % 5]:
                st.image(img_url, use_container_width=True)
                if st.checkbox(f"Pexels #{idx+1}", key=f"pexels_{idx}"):
                    selected.append((img_url, photo_url))
    else:
        st.warning("Pexels API 오류")
    return selected

# 🔃 ZIP 파일 생성
def create_zip(images, zip_name="selected_images.zip"):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, (url, origin_link) in enumerate(images):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    ext = url.split(".")[-1].split("?")[0]
                    img_data = response.content
                    filename = f"image_{idx+1}.{ext}"
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
    with st.spinner("이미지를 검색 중입니다..."):
        selected_images = []
        selected_images += search_unsplash(keyword, count)
        selected_images += search_pixabay(keyword, count)
        selected_images += search_pexels(keyword, count)

    if selected_images:
        st.markdown("---")
        st.success(f"선택한 이미지 수: {len(selected_images)}")
        if st.button("📦 선택한 이미지 ZIP 다운로드"):
            zip_file = create_zip(selected_images)
            st.download_button("📁 ZIP 파일 저장", zip_file.getvalue(), file_name="selected_images.zip", mime="application/zip")
    else:
        st.warning("선택된 이미지가 없습니다.")
