"""
🤝 장사친구 - 내 가게 맞춤 전략 공장
================================
분석 → 전략 → 전술 → 콘텐츠, 한 번에
BigContest 2025 출품작
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="장사친구 - 내 가게 맞춤 전략 공장",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Custom CSS - 발랄한 디자인
# ============================================================================

st.markdown("""
<style>
    /* 전체 배경 그라데이션 */
    .stApp {
        background: white;
    
    /* 메인 컨테이너 */
    .main-container {
        background: white;
        border-radius: 30px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 2rem auto;
        max-width: 1400px;
    }
    
    /* 히어로 섹션 */
    .hero-section {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        animation: fadeInDown 1s ease-out;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 2rem;
        opacity: 0.95;
        animation: fadeInUp 1s ease-out;
    }
    
    /* 기능 카드 */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px solid #f0f0f0;
        transition: all 0.3s ease;
        height: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        display: block;
        animation: bounce 2s infinite;
    }
    
    .feature-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    .feature-desc {
        font-size: 1.1rem;
        color: #666;
        line-height: 1.6;
    }
    
    /* 통계 카드 */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: scale(1.05);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* 프로세스 스텝 */
    .process-step {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        margin: 0 auto 1rem;
        box-shadow: 0 8px 20px rgba(245, 87, 108, 0.4);
    }
    
    .process-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .process-desc {
        font-size: 1rem;
        color: #666;
        text-align: center;
        line-height: 1.5;
    }
    
    /* 버튼 스타일 */
    .cta-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 3rem;
        border-radius: 50px;
        font-size: 1.3rem;
        font-weight: bold;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        display: inline-block;
        text-decoration: none;
    }
    
    .cta-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }
    
    /* 애니메이션 */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    /* 배지 */
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.5rem;
    }
    
    .badge-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    /* 타임라인 */
    .timeline-item {
        position: relative;
        padding-left: 3rem;
        margin-bottom: 2rem;
    }
    
    .timeline-item::before {
        content: '✓';
        position: absolute;
        left: 0;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Hero Section - 온보딩 메시지
# ============================================================================

st.markdown("""
<div class='hero-section'>
    <div style='font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; opacity: 0.9;'>
        BigContest 2025 출품작
    </div>
    <div class='hero-title'>🤝 장사친구</div>
    <div class='hero-subtitle'>내 가게 맞춤 전략 공장</div>
    <div style='font-size: 1.8rem; font-weight: 500; margin: 1.5rem 0; opacity: 0.95;'>
        분석 → 전략 → 전술 → 콘텐츠, 한 번에
    </div>
    <div style='margin-top: 2rem;'>
        <span class='badge badge-primary'>📊 우리 가게 분석</span>
        <span class='badge badge-success'>🎯 AI 전략 수립</span>
        <span class='badge badge-warning'>⚡ 즉시 실행 가능</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 온보딩: 사장님, 이렇게 시작하세요!
# ============================================================================

st.markdown("""
<div style='background: linear-gradient(135deg, #FFE5B4 0%, #FFB347 100%); 
            padding: 2.5rem; 
            border-radius: 20px; 
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(255, 179, 71, 0.3);'>
    <h2 style='text-align: center; color: #333; font-size: 2.2rem; margin-bottom: 1.5rem;'>
        👋 사장님, 장사친구가 도와드릴게요!
    </h2>
    <p style='text-align: center; font-size: 1.3rem; color: #555; line-height: 1.8;'>
        <strong>우리 가게 데이터</strong>로 <strong>대시보드</strong>에서 인사이트를 얻고,<br>
        <strong>AI</strong>가 맞춤 전략을 짜드립니다!
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 장사친구가 만드는 변화
# ============================================================================

st.markdown("## 💪 장사친구가 만드는 변화")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>10초</div>
        <div class='stat-label'>내 가게 분석 완료</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>3분</div>
        <div class='stat-label'>맞춤 전략 생성</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>즉시</div>
        <div class='stat-label'>실행 가능한 전술</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='stat-card'>
        <div class='stat-number'>24/7</div>
        <div class='stat-label'>AI가 함께 고민</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# 이렇게 시작하세요!
# ============================================================================

st.markdown("## 🚀 이렇게 시작하세요!")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <span class='feature-icon'>📊</span>
        <div class='feature-title'>1단계: 대시보드</div>
        <div class='feature-desc'>
            <strong>우리 가게 인사이트 확인</strong><br><br>
            • 경쟁사 대비 우리 위치는?<br>
            • 어떤 고객이 많이 오나?<br>
            • 재방문율은 어때?<br>
            • 강점과 약점은 뭐지?<br><br>
            <strong>👈 좌측 메뉴: Dashboard</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <span class='feature-icon'>🎯</span>
        <div class='feature-title'>2단계: AI 전략</div>
        <div class='feature-desc'>
            <strong>맞춤 마케팅 전략 생성</strong><br><br>
            • 우리 가게만의 STP 전략<br>
            • 4P 기반 실행 계획<br>
            • 날씨/이벤트 대응 전술<br>
            • SNS 콘텐츠 가이드<br><br>
            <strong>👈 좌측 메뉴: App</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-card'>
        <span class='feature-icon'>⚡</span>
        <div class='feature-title'>3단계: 바로 실행</div>
        <div class='feature-desc'>
            <strong>즉시 사용 가능한 결과물</strong><br><br>
            • 오늘 당장 쓸 프로모션<br>
            • 인스타그램 포스팅 문구<br>
            • 이벤트 기획안<br>
            • 메뉴 개선 제안<br><br>
            <strong>💡 복사해서 바로 사용!</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# 이렇게 사용하세요
# ============================================================================

st.markdown("## 🔄 3분이면 끝! 사용법")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='process-step'>1</div>
    <div class='process-title'>가게 선택</div>
    <div class='process-desc'>내 가맹점을<br>선택합니다</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='process-step'>2</div>
    <div class='process-title'>대시보드 확인</div>
    <div class='process-desc'>현황과 문제점을<br>파악합니다</div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='process-step'>3</div>
    <div class='process-title'>AI에게 질문</div>
    <div class='process-desc'>원하는 전략을<br>요청합니다</div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='process-step'>4</div>
    <div class='process-title'>바로 실행</div>
    <div class='process-desc'>결과물을 복사해<br>바로 사용합니다</div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# 장사친구의 마법 🪄
# ============================================================================

st.markdown("## 🪄 장사친구가 일하는 방식")

# 시스템 구성 Sankey 다이어그램
fig = go.Figure(data=[go.Sankey(
    node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "white", width = 0.5),
        label = ["📊 우리 가게 데이터", "🔍 대시보드 분석", "🤖 AI 분석", 
                 "💡 인사이트 발견", "🎯 맞춤 전략", "⚡ 실행 전술",
                 "📱 콘텐츠 생성", "✅ 바로 사용!"],
        color = ["#667eea", "#764ba2", "#f093fb", "#56ab2f", "#f5576c", "#ffa500", "#2ecc71", "#3498db"]
    ),
    link = dict(
        source = [0, 0, 1, 2, 1, 2, 3, 3, 4, 5, 6],
        target = [1, 2, 3, 3, 4, 5, 4, 6, 7, 7, 7],
        value = [5, 5, 3, 3, 4, 4, 3, 3, 4, 4, 3],
        color = ["rgba(102,126,234,0.3)"] * 11
    )
)])

fig.update_layout(
    title_text="우리 가게 데이터 → AI 분석 → 바로 쓰는 전략",
    font_size=14,
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# 대시보드에서 이런 걸 알 수 있어요
# ============================================================================

st.markdown("## 📊 대시보드에서 이런 걸 알 수 있어요")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🏆 우리 가게 경쟁력
    <div class='timeline-item'>
        <strong>시장 내 위치 확인</strong><br>
        같은 업종에서 몇 등일까? 우리 상권에서는?
    </div>
    <div class='timeline-item'>
        <strong>고객 충성도 분석</strong><br>
        재방문하는 손님이 몇 %나 될까?
    </div>
    <div class='timeline-item'>
        <strong>성장 가능성 진단</strong><br>
        신규 고객은 계속 들어오고 있나?
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### 💰 돈 되는 인사이트
    <div class='timeline-item'>
        <strong>수익성 체크</strong><br>
        객단가와 매출, 취소율은 괜찮나?
    </div>
    <div class='timeline-item'>
        <strong>배달 활용도</strong><br>
        배달 매출 비중은? 더 늘릴 수 있나?
    </div>
    <div class='timeline-item'>
        <strong>안정성 평가</strong><br>
        우리 업종 폐업률은? 우리는 안전한가?
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# 기술 스택
# ============================================================================

st.markdown("## 🛠️ 기술 스택")

tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)

with tech_col1:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);'>
        <h3>🤖 AI/ML</h3>
        <p>Gemini 2.5 Flash<br>Langchain<br>Langgraph</p>
    </div>
    """, unsafe_allow_html=True)

with tech_col2:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%); border-radius: 15px; color: white; box-shadow: 0 8px 20px rgba(86, 171, 47, 0.3);'>
        <h3>📊 데이터</h3>
        <p>Pandas<br>NumPy<br>CSV/JSON</p>
    </div>
    """, unsafe_allow_html=True)

with tech_col3:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; color: white; box-shadow: 0 8px 20px rgba(245, 87, 108, 0.3);'>
        <h3>📈 시각화</h3>
        <p>Plotly<br>Streamlit<br>Interactive Charts</p>
    </div>
    """, unsafe_allow_html=True)

with tech_col4:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #ffa500 0%, #ff6348 100%); border-radius: 15px; color: white; box-shadow: 0 8px 20px rgba(255, 165, 0, 0.3);'>
        <h3>🌐 외부 API</h3>
        <p>기상청 API<br>공공데이터 API<br>위치 기반 서비스</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# CTA Section
# ============================================================================

st.markdown("""
<div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin: 2rem 0;'>
    <h2 style='margin-bottom: 1rem; font-size: 2.5rem;'>🤝 장사친구와 함께 시작할까요?</h2>
    <p style='font-size: 1.5rem; margin-bottom: 2rem; opacity: 0.95;'>
        어렵게 생각하지 마세요!<br>
        왼쪽 메뉴에서 클릭 몇 번이면 끝입니다
    </p>
    <div style='margin-top: 2.5rem; background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 15px;'>
        <div style='font-size: 1.8rem; font-weight: bold; margin-bottom: 1.5rem;'>
            👇 지금 바로 시작하기
        </div>
        <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
            <div style='background: rgba(255,255,255,0.2); padding: 1.5rem 2rem; border-radius: 15px; flex: 1; min-width: 250px; max-width: 400px;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>📊</div>
                <div style='font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;'>1단계</div>
                <div style='font-size: 1.1rem;'>👈 Dashboard 메뉴<br>우리 가게 현황 파악</div>
            </div>
            <div style='background: rgba(255,255,255,0.2); padding: 1.5rem 2rem; border-radius: 15px; flex: 1; min-width: 250px; max-width: 400px;'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🤖</div>
                <div style='font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;'>2단계</div>
                <div style='font-size: 1.1rem;'>👈 App 메뉴<br>AI한테 전략 요청</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================

st.markdown("<br>", unsafe_allow_html=True)

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"""
<div style='text-align: center; color: #666; padding: 2rem; border-top: 2px solid #f0f0f0; margin-top: 3rem;'>
    <p style='font-size: 1.3rem; margin-bottom: 1rem; font-weight: bold; color: #667eea;'>
        🏆 BigContest 2025 출품작
    </p>
    <p style='font-size: 1.2rem; margin-bottom: 1rem;'>
        <strong>팀명: 장사친구</strong>
    </p>
    <p style='font-size: 1rem; color: #888; margin-bottom: 0.5rem;'>
        분석 → 전략 → 전술 → 콘텐츠, 한 번에
    </p>
    <p style='font-size: 0.95rem; color: #999; margin-bottom: 1rem;'>
        Powered by Langchain, Langgraph, and Gemini 2.5 Flash
    </p>
    <p style='font-size: 0.85rem; color: #aaa;'>
        마지막 업데이트: {current_time}
    </p>
    <div style='margin-top: 1.5rem;'>
        <span style='margin: 0 0.5rem; font-size: 1.5rem;'>🤝</span>
        <span style='margin: 0 0.5rem; font-size: 1.5rem;'>📊</span>
        <span style='margin: 0 0.5rem; font-size: 1.5rem;'>🤖</span>
        <span style='margin: 0 0.5rem; font-size: 1.5rem;'>💡</span>
        <span style='margin: 0 0.5rem; font-size: 1.5rem;'>🚀</span>
    </div>
</div>
""", unsafe_allow_html=True)