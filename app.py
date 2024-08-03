import streamlit as st
import pdfplumber
import pandas as pd
import re
import zipfile
import os

# PDF에서 작성일자 추출 함수
def extract_written_date_from_pdf(pdf_path):
    written_date = None
    # 다양한 형식의 작성일자를 처리하기 위한 정규 표현식
    date_pattern = re.compile(r'작성일자.*?(\d{4})\D+(\d{1,2})\D+(\d{1,2})')
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                match = date_pattern.search(text)
                if match:
                    year, month, day = match.groups()
                    written_date = f"{year}-{int(month):02d}-{int(day):02d}"
                    break
    return written_date

# 파일명 파싱 함수
def parse_filename(filename, written_date):
    # 파일명을 해싱 문자열 없이 제목과 확장자로 분리
    title, ext = filename.rsplit('.', 1)
    title_parts = title.split(' ')
    hash_removed_title = ' '.join(title_parts[:-1])  # 마지막 부분이 해싱 문자열이라고 가정
    # 새로운 제목 형식으로 반환
    return f"{written_date} {hash_removed_title}.{ext}"

st.title("PDF 작성일자 추출기")

uploaded_files = st.file_uploader("PDF 파일을 선택하세요", accept_multiple_files=True, type="pdf")

if uploaded_files:
    data = {"파일명": [], "작성일자": [], "새로운 제목": []}
    valid_files = []

    for uploaded_file in uploaded_files:
        written_date = extract_written_date_from_pdf(uploaded_file)
        if written_date:
            data["파일명"].append(uploaded_file.name)
            data["작성일자"].append(written_date)
            new_title = parse_filename(uploaded_file.name, written_date)
            data["새로운 제목"].append(new_title)
            valid_files.append((uploaded_file, new_title))
        else:
            data["파일명"].append(uploaded_file.name)
            data["작성일자"].append("작성일자 없음")
            data["새로운 제목"].append("작성일자 없음")
    
    df = pd.DataFrame(data)

    st.subheader("추출된 작성일자 및 파싱된 제목")
    st.dataframe(df)

    # 파일을 ZIP으로 압축
    with zipfile.ZipFile("files.zip", 'w') as zipf:
        for uploaded_file, new_title in valid_files:
            with open(new_title, "wb") as f:
                f.write(uploaded_file.getbuffer())
            zipf.write(new_title)
            os.remove(new_title)

    with open("files.zip", "rb") as f:
        btn = st.download_button(
            label="ZIP 파일 다운로드",
            data=f,
            file_name="files.zip",
            mime="application/zip"
        )
        
else:
    st.write("PDF 파일을 업로드 해주세요.")