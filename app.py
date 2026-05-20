# app.py
import streamlit as st
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()

from pipeline import process_video

st.set_page_config(page_title='인플루언서 영상 분석기', page_icon='🎬', layout='wide')
st.title('🎬 인플루언서 영상 분석기')

# --- 입력 섹션 ---
with st.form('input_form'):
    links_input = st.text_area(
        '영상 링크 입력 (한 줄에 하나씩)',
        height=200,
        placeholder='https://www.tiktok.com/@...\nhttps://www.instagram.com/reel/...'
    )
    product_category = st.text_input('제품군 (선택사항)', placeholder='아이패치, 토너패드, 클렌저 등')
    submitted = st.form_submit_button('🚀 분석 시작', type='primary')

if submitted:
    links = [l.strip() for l in links_input.strip().splitlines() if l.strip()]
    if not links:
        st.warning('링크를 하나 이상 입력해 주세요.')
        st.stop()

    results = []
    progress_bar = st.progress(0)
    status_container = st.container()

    for i, url in enumerate(links):
        with status_container:
            st.write(f'⏳ 처리 중... ({i+1}/{len(links)}) `{url[:60]}...`')
        if i > 0:
            time.sleep(5)
        result = process_video(url, product_category)
        results.append(result)
        progress_bar.progress((i + 1) / len(links))

    status_container.success(f'✅ {len(links)}개 영상 분석 완료!')
    st.session_state['results'] = results

# --- 결과 섹션 ---
if 'results' in st.session_state and st.session_state['results']:
    df = pd.DataFrame(st.session_state['results'])

    st.subheader('📊 분석 결과 (클릭해서 수정 가능)')

    error_mask = df['오류'] != ''
    if error_mask.any():
        st.warning(f'⚠️ {error_mask.sum()}개 영상 처리 실패. 오류 컬럼 확인하세요.')

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows='dynamic',
        column_config={
            '전체플로우': st.column_config.TextColumn(width='large'),
            '오류': st.column_config.TextColumn(width='medium'),
        }
    )

    csv_cols = ['소재명', '제품군', '보이스', '자막/텍스트유무', '3초훅',
                '할인소구', '초반문제제시', '콘텐츠톤', '제품등장타이밍', '전체플로우']
    export_df = edited_df[csv_cols]

    csv_bytes = export_df.to_csv(index=False).encode('utf-8-sig')

    st.download_button(
        label='📥 CSV 다운로드 (구글 시트에 붙여넣기용)',
        data=csv_bytes,
        file_name='influencer_analysis.csv',
        mime='text/csv',
    )

    st.caption('💡 구글 시트에서: 파일 → 가져오기 → 업로드 → CSV 선택')
