import streamlit as st
import requests
import os
import shutil
import zipfile
from urllib.parse import quote
from PIL import Image
from io import BytesIO

# API 키
UNSPLASH_KEY = "j5lyiOKj0bj6iMFPgvCnO0cCB_eWEyx5NsXZr3VRR94"
PEXELS_KEY = "kd1frTIFwfExQIR5DIGn1eKJ7gEGUIbbWDKSmi3sLjGhv9nDVP0Qmnnh"
PIXABAY_KEY = "51462455-6f4af1014e035b145b2e7731b"

# 다운로드 폴더
DOWNLOAD_DIR = "images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 이미지 검색 함수
def search_unsplash(keyword, count):
    url = f"https://api.unsplash.com/search/photos?query={quote(keyword)}&per_page={count}"
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    res = requests.get(url, headers=headers)
    data = res.json()
    return [(img['urls']['small'], 'Unsplash') for img in data.get('results', [])]

def search_pexels(keyword, count):
    try:
        headers = {"Authorization": PEXELS_KEY}
        url = f"https://api.pexels.com/v1/search?query={quote(keyword)}&per_page={count}"
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        return [(img['src']['medium'], 'Pexels') for img in data.get('photos', [])]
    except Exception:
        return []

def search_pixabay(keyword, count):
    try:
        url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={quote(keyword)}&image_type=photo&per_page={count}"
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return [(img['webformatURL'], 'Pixabay') for img in data.get('hits', [])]
    except Exception:
        return []

# 이미지 다운로드 및 저장
def download_images(image_list):
    saved_paths = []
    for i, (url, source) in enumerate(image_list):
        try:
            response = requests.get(url, stream=True)
            image = Image.open(BytesIO(response.content))
            filename = f"{source}_{i+1}.jpg"
            path = os.path.join(DOWNLOAD_DIR, filename)
            image.save(path)
            saved_paths.append((path, source))
        except Exception as e:
            print(f"Error downloading {url}: {e}")
    return saved_paths

# 이미지 압축(zip)
def zip_images():
    zip_path = "images.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(DOWNLOAD_DIR):
            f_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(f_path):
                zipf.write(f_path, filename)
    return zip_path

# Streamlit UI
st.set_page_config(page_title="멀티 이미지 수집기", layout="wide")
st.title("📸 이미지 검색 통합 도구")

keyword = st.text_input("검색어를 입력하세요:", "제주도")
count = st.slider("API별 이미지 개수", 1, 20, 10)

if st.button("🔍 이미지 검색"):
    # 이전 결과 삭제
    for f in os.listdir(DOWNLOAD_DIR):
        try:
            os.remove(os.path.join(DOWNLOAD_DIR, f))
        except:
            pass

    all_images = []

    st.subheader("🖼 Unsplash")
    unsplash_images = search_unsplash(keyword, count)
    if unsplash_images:
        cols = st.columns(5)
        for i, (url, _) in enumerate(unsplash_images):
            with cols[i % 5]:
                st.image(url, caption=f"Unsplash #{i+1}", use_container_width=True)
    all_images.extend(unsplash_images)

    st.subheader("📷 Pixabay")
    pixabay_images = search_pixabay(keyword, count)
    if pixabay_images:
        cols = st.columns(5)
        for i, (url, _) in enumerate(pixabay_images):
            with cols[i % 5]:
                st.image(url, caption=f"Pixabay #{i+1}", use_container_width=True)
    else:
        st.warning("Pixabay에서 이미지를 가져올 수 없습니다.")
    all_images.extend(pixabay_images)

    st.subheader("📷 Pexels")
    pexels_images = search_pexels(keyword, count)
    if pexels_images:
        cols = st.columns(5)
        for i, (url, _) in enumerate(pexels_images):
            with cols[i % 5]:
                st.image(url, caption=f"Pexels #{i+1}", use_container_width=True)
    else:
        st.warning("Pexels에서 이미지를 가져올 수 없습니다.")
    all_images.extend(pexels_images)

    # 이미지 저장 & 다운로드 링크
    if all_images:
        saved = download_images(all_images)
        zip_file = zip_images()
        with open(zip_file, "rb") as f:
            st.download_button("📦 이미지 ZIP 다운로드", f, file_name="images.zip")
