"""
마케팅 대시보드 페이지
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path

def load_data():
    """데이터 로드"""
    try:
        base_path = Path(__file__).parent.parent.parent
        flow_df = pd.read_csv(base_path / 'data/유동인구.csv')
        rent_df = pd.read_csv(base_path / 'data/임대료.csv')
        integrated_df = pd.read_csv(base_path / 'data/통합_제공데이터.csv')
        # 기준일ID를 날짜로 변환
        if '기준일ID' in flow_df.columns:
            flow_df['기준일자'] = pd.to_datetime(flow_df['기준일ID'].astype(str), format='%Y%m%d', errors='coerce')
        
        # 기준년월을 날짜로 변환 (다양한 형식 지원)
        if '기준년월' in integrated_df.columns:
            # ISO8601 형식도 지원 (YYYY-MM-DD, YYYY-MM 등)
            integrated_df['기준년월'] = pd.to_datetime(integrated_df['기준년월'], format='ISO8601', errors='coerce')
        
        return flow_df, rent_df, integrated_df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None, None, None
def get_store_district_code(store_info, flow_df):
    """가맹점 주소로부터 행정동코드 매칭"""
    store_address = str(store_info.get('가맹점주소', ''))
    
    if '행정동' in flow_df.columns:
        for idx, row in flow_df[['행정동코드', '행정동']].drop_duplicates().iterrows():
            dong_name = str(row['행정동'])
            if dong_name in store_address:
                return row['행정동코드']
    
    return flow_df['행정동코드'].iloc[0] if len(flow_df) > 0 else None

def create_business_strength_radar(df, store_id):
    """비즈니스 강점 분석 레이더 차트 + 상세 인사이트"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None, None, None
    
    recent_data = store_data.sort_values('기준년월').iloc[-1]
    
    # NaN 값을 안전하게 처리하는 헬퍼 함수
    def safe_get(value, default=0):
        return value if pd.notna(value) else default
    
    # 1️⃣ 시장 경쟁력 (Market Competitiveness)
    market_rank_industry = 100 - safe_get(recent_data.get('동일 업종 내 매출 순위 비율'), 50)
    market_rank_area = 100 - safe_get(recent_data.get('동일 상권 내 매출 순위 비율'), 50)
    sales_vs_industry = safe_get(recent_data.get('동일 업종 매출금액 비율'), 100)
    market_competitiveness = (market_rank_industry + market_rank_area + min(sales_vs_industry, 150)) / 3
    
    # 2️⃣ 고객 충성도 (Customer Loyalty)
    retention = safe_get(recent_data.get('재방문 고객 비중'), 0)
    stable_customer = safe_get(recent_data.get('거주 이용 고객 비율'), 0) + safe_get(recent_data.get('직장 이용 고객 비율'), 0)
    customer_loyalty = (retention * 0.7 + stable_customer * 0.3)
    
    # 3️⃣ 성장 잠재력 (Growth Potential)
    new_customer = safe_get(recent_data.get('신규 고객 비중'), 0)
    flow_usage = safe_get(recent_data.get('유동인구 이용 고객 비율'), 0)
    operation_months = safe_get(recent_data.get('가맹점 운영개월수 구간'), 3)
    growth_score = (7 - operation_months) / 6 * 100
    growth_potential = (new_customer * 0.5 + flow_usage * 0.3 + growth_score * 0.2)
    
    # 4️⃣ 수익성 (Profitability)
    price_level = (7 - safe_get(recent_data.get('객단가 구간'), 3)) / 6 * 100
    sales_level = (7 - safe_get(recent_data.get('매출금액 구간'), 3)) / 6 * 100
    cancel_rate = safe_get(recent_data.get('취소율 구간'), 3)
    cancel_score = (7 - cancel_rate) / 6 * 100
    profitability = (price_level * 0.4 + sales_level * 0.4 + cancel_score * 0.2)
    
    # 5️⃣ 디지털 활용도 (Digital Utilization)
    delivery_ratio = safe_get(recent_data.get('배달매출금액 비율'), 0)
    digital_utilization = min(delivery_ratio * 2, 100)
    
    # 6️⃣ 사업 안정성 (Business Stability)
    operation_stability = min(operation_months / 6 * 100, 100)
    industry_closure = safe_get(recent_data.get('동일 업종 내 해지 가맹점 비중'), 0)
    area_closure = safe_get(recent_data.get('동일 상권 내 해지 가맹점 비중'), 0)
    closure_risk = 100 - ((industry_closure + area_closure) / 2)
    business_stability = (operation_stability * 0.6 + closure_risk * 0.4)
    
    # 최종 지표
    metrics = {
        '시장 경쟁력': market_competitiveness,
        '고객 충성도': customer_loyalty,
        '성장 잠재력': growth_potential,
        '수익성': profitability,
        '디지털 활용': digital_utilization,
        '사업 안정성': business_stability
    }
    
    # 전체 평균 계산 (NaN 안전하게 처리)
    avg_metrics = {
        '시장 경쟁력': 50,
        '고객 충성도': safe_get(df['재방문 고객 비중'].mean(), 50),
        '성장 잠재력': safe_get(df['신규 고객 비중'].mean(), 50),
        '수익성': 50,
        '디지털 활용': safe_get(df['배달매출금액 비율'].mean() * 2, 50),
        '사업 안정성': 50
    }
    
    # 상세 설명 생성
    metric_explanations = {
        '시장 경쟁력': f"""
**산출 기준:**
- 업종 내 순위: {market_rank_industry:.1f}점 (상위 {100-market_rank_industry:.1f}%)
- 상권 내 순위: {market_rank_area:.1f}점 (상위 {100-market_rank_area:.1f}%)
- 업종 대비 매출: {sales_vs_industry:.1f}% (업종 평균=100)

**해석:** 동종 업체 및 상권 내에서의 상대적 위치를 종합 평가
""",
        '고객 충성도': f"""
**산출 기준:**
- 재방문 고객: {retention:.1f}% (가중치 70%)
- 안정 고객층: {stable_customer:.1f}% (거주+직장, 가중치 30%)

**해석:** 반복 구매 성향이 높은 안정적 고객 기반 평가
""",
        '성장 잠재력': f"""
**산출 기준:**
- 신규 고객 비중: {new_customer:.1f}% (가중치 50%)
- 유동인구 활용: {flow_usage:.1f}% (가중치 30%)
- 신규성 점수: {growth_score:.1f}점 (운영 {operation_months}개월 구간, 가중치 20%)

**해석:** 신규 고객 유입 및 확장 가능성 평가
""",
        '수익성': f"""
**산출 기준:**
- 객단가 수준: {price_level:.1f}점 (구간 {safe_get(recent_data.get('객단가 구간'), 3)}/6, 가중치 40%)
- 매출 규모: {sales_level:.1f}점 (구간 {safe_get(recent_data.get('매출금액 구간'), 3)}/6, 가중치 40%)
- 취소율: {cancel_score:.1f}점 (구간 {cancel_rate}/6, 가중치 20%)

**해석:** 거래당 수익성과 매출 안정성 종합 평가
""",
        '디지털 활용': f"""
**산출 기준:**
- 배달 매출 비율: {delivery_ratio:.1f}%
- 정규화 점수: {digital_utilization:.1f}점 (50% 이상 시 만점)

**해석:** 배달 플랫폼 등 디지털 채널 활용도
""",
        '사업 안정성': f"""
**산출 기준:**
- 운영 지속성: {operation_stability:.1f}점 (운영 {operation_months}개월 구간, 가중치 60%)
- 폐업 리스크: {closure_risk:.1f}점 (업종 {industry_closure:.1f}%, 상권 {area_closure:.1f}% 대비, 가중치 40%)

**해석:** 장기 운영 가능성 및 시장 안정성 평가
"""
    }
    
    # 인사이트 생성
    categories = list(metrics.keys())
    store_values = [safe_get(v, 50) for v in metrics.values()]  # NaN 방지
    avg_values = [safe_get(avg_metrics[k], 50) for k in categories]  # NaN 방지
    
    insights = []
    strengths = []
    weaknesses = []
    
    for cat, store_val, avg_val in zip(categories, store_values, avg_values):
        diff = store_val - avg_val
        if diff > 15:
            strengths.append(f"{cat}: {store_val:.1f}점 (평균 대비 +{diff:.1f}점)")
        elif diff < -15:
            weaknesses.append(f"{cat}: {store_val:.1f}점 (평균 대비 {diff:.1f}점)")
    
    # 종합 평가 (NaN 방지)
    overall_score = safe_get(sum(store_values) / len(store_values) if len(store_values) > 0 else 50, 50)
    avg_score = safe_get(sum(avg_values) / len(avg_values) if len(avg_values) > 0 else 50, 50)

    if overall_score >= 70:
        grade = "우수"
        grade_color = "#78FB71"
        grade_bg = "#E8FDE8"
        grade_emoji = "🏆"
        comment = "전반적으로 경쟁력이 뛰어난 매장입니다. 현재 강점을 유지하면서 약점 보완에 집중하세요."
    elif overall_score >= 50:
        grade = "양호"
        grade_color = "#66B0FF"
        grade_bg = "#E3F2FD"
        grade_emoji = "✅"
        comment = "평균 수준의 안정적인 운영 중입니다. 핵심 지표 개선으로 한 단계 도약이 가능합니다."
    else:
        grade = "개선 필요"
        grade_color = "#FF6B6B"
        grade_bg = "#FFE8E8"
        grade_emoji = "⚠️"
        comment = "여러 핵심 지표에서 개선이 필요합니다. 우선순위를 정해 단계적으로 개선하세요."

    summary = f"""
    <div style="padding: 20px; border-radius: 12px; background-color: #f8f9fa; margin-bottom: 20px; border-left: 5px solid {grade_color};">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px;">
            <h5 style="margin: 0; display: inline;">📊 종합 평가 : 
            <div style="display: inline-block; padding: 8px 16px; border-radius: 8px; background-color: {grade_bg};">
                <span style="font-size: 18px; font-weight: bold; color: {grade_color};">{grade_emoji} {grade}</span>
            </div> </h5>
        </div>
            <div style="flex: 2; min-width: 300px; display: flex; gap: 30px; align-items: center;">
                <div>
                    <strong>종합 점수</strong>: <span style="font-size: 18px; font-weight: bold; color: {grade_color};">{overall_score:.1f}점</span> / 100점
                </div>
                <div>
                    <strong>전체 평균</strong>: {avg_score:.1f}점
                </div>
                <div>
                    <strong>평균 대비</strong>: <span style="color: {'#2ca02c' if overall_score >= avg_score else '#d62728'}; font-weight: bold; font-size: 16px;">{overall_score - avg_score:+.1f}점</span>
                </div>
            </div>
        </div>
        <p style="margin: 15px 0 0 0; color: #555; border-top: 1px solid #ddd; padding-top: 10px;">
            💡 {comment}
        </p>
    """

    # Plotly 레이더 차트
    fig = go.Figure()
    
    # 평균선
    fig.add_trace(go.Scatterpolar(
        r=avg_values + [avg_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='전체 평균',
        line=dict(color='lightgray', width=2),
        fillcolor='rgba(200, 200, 200, 0.2)',
        hovertemplate='<b>%{theta}</b><br>평균: %{r:.1f}점<extra></extra>'
    ))
    
    # 가맹점 데이터
    fig.add_trace(go.Scatterpolar(
        r=store_values + [store_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='현재 매장',
        line=dict(color='#66B0FF', width=3),
        fillcolor='rgba(102, 176, 255, 0.3)',
        hovertemplate='<b>%{theta}</b><br>점수: %{r:.1f}점<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                tickfont=dict(size=10),
                tickmode='linear',
                tick0=0,
                dtick=20
            ),
            angularaxis=dict(
                tickfont=dict(size=11)
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        title=f'<b>비즈니스 강점 분석</b><br><sub>종합 점수: {overall_score:.1f}점 ({grade})</sub>',
        height=450,
        margin=dict(t=100, b=80, l=80, r=80)
    )
    
    return fig, summary, metric_explanations




def create_sales_trend_comparison(df, store_id):
    """매출 추이 비교 레이더 차트 (업종/상권 평균 비교)"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None, None, None, None
    
    store_data = store_data.sort_values('기준년월')
    recent_data = store_data.iloc[-1]
    
    # 업종 및 상권 정보
    industry = recent_data.get('업종', None)
    area = recent_data.get('상권', None)
    
    # 3개 그룹으로 나눔
    group1 = ['배달매출금액 비율', '동일 업종 매출금액 비율', '동일 업종 매출건수 비율',
              '동일 업종 내 매출 순위 비율', '동일 상권 내 매출 순위 비율']
    
    group2 = ['매출금액 구간', '매출건수 구간', '유니크 고객 수 구간', 
              '객단가 구간', '취소율 구간']
    
    group3 = ['재방문 고객 비중', '신규 고객 비중', '거주 이용 고객 비율', 
              '직장 이용 고객 비율', '유동인구 이용 고객 비율']
    
    groups = [group1, group2, group3]
    titles = ['🏆 경쟁력 지표', '📊 운영 지표', '👥 고객 구성']
    subtexts = ['(업종/상권 평균 대비)', '(1=우수, 6=부진)', '(고객 비중 %)']
    
    # 평균 계산 (업종 또는 상권)
    if industry:
        comparison_df = df[df['업종'] == industry]
        comparison_label = f'{industry} 평균'
    elif area:
        comparison_df = df[df['상권'] == area]
        comparison_label = f'{area} 평균'
    else:
        comparison_df = df
        comparison_label = '전체 평균'
    
    avg_data = comparison_df.mean(numeric_only=True)
    
    # 각 그룹별 레이더 차트 생성 함수
    def create_single_radar(cols, title, subtext):
        # 유효한 컬럼만 선택
        valid_cols = [c for c in cols if c in recent_data.index and pd.notna(recent_data.get(c))]
        
        if len(valid_cols) == 0:
            return None
        
        store_vals = recent_data[valid_cols].astype(float).values
        mean_vals = avg_data[valid_cols].astype(float).values
        
        # 구간 지표는 역전환 (1이 좋음, 6이 나쁨 -> 역전)
        if '구간' in title or '구간' in subtext:
            store_vals = 7 - store_vals
            mean_vals = 7 - mean_vals
        
        # 순위 비율도 역전환 (낮을수록 좋음)
        if '순위' in ' '.join(valid_cols):
            store_vals_adj = []
            mean_vals_adj = []
            for i, col in enumerate(valid_cols):
                if '순위' in col:
                    store_vals_adj.append(100 - store_vals[i])
                    mean_vals_adj.append(100 - mean_vals[i])
                else:
                    store_vals_adj.append(store_vals[i])
                    mean_vals_adj.append(mean_vals[i])
            store_vals = np.array(store_vals_adj)
            mean_vals = np.array(mean_vals_adj)
        
        # 라벨 단축
        short_labels = {
            '배달매출금액 비율': '배달매출',
            '동일 업종 매출금액 비율': '업종매출',
            '동일 업종 매출건수 비율': '업종건수',
            '동일 업종 내 매출 순위 비율': '업종순위',
            '동일 상권 내 매출 순위 비율': '상권순위',
            '매출금액 구간': '매출규모',
            '매출건수 구간': '거래건수',
            '유니크 고객 수 구간': '고객수',
            '객단가 구간': '객단가',
            '취소율 구간': '취소율',
            '재방문 고객 비중': '재방문',
            '신규 고객 비중': '신규고객',
            '거주 이용 고객 비율': '거주고객',
            '직장 이용 고객 비율': '직장고객',
            '유동인구 이용 고객 비율': '유동인구'
        }
        
        labels = [short_labels.get(c, c) for c in valid_cols]
        
        fig = go.Figure()
        
        # 평균선
        fig.add_trace(go.Scatterpolar(
            r=mean_vals.tolist() + [mean_vals[0]],
            theta=labels + [labels[0]],
            fill='toself',
            name=comparison_label,
            line=dict(color='lightgray', width=2),
            fillcolor='rgba(200, 200, 200, 0.25)',
            hovertemplate='<b>%{theta}</b><br>' + comparison_label + ': %{r:.1f}<extra></extra>'
        ))
        
        # 가맹점 데이터
        fig.add_trace(go.Scatterpolar(
            r=store_vals.tolist() + [store_vals[0]],
            theta=labels + [labels[0]],
            fill='toself',
            name=f'가맹점 {store_id}',
            line=dict(color='#66B0FF', width=3),
            fillcolor='rgba(102, 176, 255, 0.3)',
            hovertemplate='<b>%{theta}</b><br>우리 매장: %{r:.1f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    showticklabels=True,
                    tickfont=dict(size=9)
                ),
                angularaxis=dict(
                    tickfont=dict(size=10)
                )
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            title=f'<b>{title}</b><br><sub>{subtext}</sub>',
            height=400,
            margin=dict(t=80, b=60, l=60, r=60)
        )
        
        return fig
    
    # 3개 차트 생성
    charts = []
    for cols, title, subtext in zip(groups, titles, subtexts):
        chart = create_single_radar(cols, title, subtext)
        if chart:
            charts.append((title, chart))
    
    # 인사이트 생성
    insights = []
    
    # 경쟁력 평가
    if '동일 업종 매출금액 비율' in recent_data.index:
        industry_sales = recent_data.get('동일 업종 매출금액 비율', 100)
        if industry_sales > 110:
            insights.append(f"✅ **업종 대비 매출**: {industry_sales:.1f}% (우수)")
        elif industry_sales < 90:
            insights.append(f"⚠️ **업종 대비 매출**: {industry_sales:.1f}% (개선 필요)")
    
    # 순위 평가
    if '동일 업종 내 매출 순위 비율' in recent_data.index:
        rank = recent_data.get('동일 업종 내 매출 순위 비율', 50)
        if rank <= 30:
            insights.append(f"🏆 **업종 내 순위**: 상위 {rank:.1f}%")
        elif rank > 50:
            insights.append(f"📈 **업종 내 순위**: 상위 {rank:.1f}% (순위 개선 필요)")
    
    # 고객 구성 평가
    retention = recent_data.get('재방문 고객 비중', 0)
    new_cust = recent_data.get('신규 고객 비중', 0)
    
    if retention > 50:
        insights.append(f"💎 **고객 충성도 우수**: 재방문 {retention:.1f}%")
    elif new_cust > 50:
        insights.append(f"🌱 **신규 유입 활발**: 신규고객 {new_cust:.1f}%")
    
    insight_text = "\n\n".join(insights) if insights else "인사이트 데이터 부족"
    
    # 상세 해석 텍스트 생성
    store_name = recent_data.get('가맹점명', f'가맹점 {store_id}')
    industry_sales = recent_data.get('동일 업종 매출금액 비율', 100)
    industry_rank = recent_data.get('동일 업종 내 매출 순위 비율', 50)
    area_rank = recent_data.get('동일 상권 내 매출 순위 비율', 50)
    retention = recent_data.get('재방문 고객 비중', 0)
    new_cust = recent_data.get('신규 고객 비중', 0)
    sales_section = recent_data.get('매출금액 구간', 4)
    price_section = recent_data.get('객단가 구간', 4)
    cancel_section = recent_data.get('취소율 구간', 4)
    residential = recent_data.get('거주 이용 고객 비율', 0)
    office = recent_data.get('직장 이용 고객 비율', 0)
    floating = recent_data.get('유동인구 이용 고객 비율', 0)

    # 경쟁력 분석
    if industry_sales >= 110:
        sales_comment = f"업종 평균 대비 **{industry_sales:.1f}%** 로 🔥 **우수한 성과**를 보이고 있습니다. 현재의 경쟁력을 유지하면서 시장 점유율 확대에 집중할 시점입니다."
    elif industry_sales >= 90:
        sales_comment = f"업종 평균 대비 **{industry_sales:.1f}%** 로 ✅ **평균 수준**을 유지하고 있습니다. 차별화 전략을 통해 한 단계 도약할 수 있는 기회가 있습니다."
    else:
        sales_comment = f"업종 평균 대비 **{industry_sales:.1f}%** 로 ⚠️ **개선이 필요한 상황**입니다. 메뉴 구성, 가격 정책, 마케팅 전략 등을 전면 재검토할 것을 권장합니다."

    if industry_rank <= 30:
        rank_comment = f"**{industry}** 업종 내에서 상위 **{industry_rank:.1f}%** 🏆로 **상위권**에 위치해 있습니다."
        rank_suggestion = "리더십을 유지하기 위한 지속적인 품질 관리가 중요합니다."
    elif industry_rank <= 50:
        rank_comment = f"**{industry}** 업종 내에서 상위 **{industry_rank:.1f}%** ✅로 **중위권**에 해당합니다."
        rank_suggestion = "상위권 진입을 위해 고객 경험 개선과 마케팅 강화가 필요합니다."
    else:
        rank_comment = f"**{industry}** 업종 내에서 상위 **{industry_rank:.1f}%** 📈로 **하위권**에 머물고 있어 개선이 시급합니다."
        rank_suggestion = "경쟁사 벤치마킹과 차별화된 가치 제안을 통해 순위 개선에 집중해야 합니다."

    if area_rank <= 30:
        area_comment = f"**{area}** 상권 내에서는 상위 **{area_rank:.1f}%** 로 지역 내 입지가 견고합니다."
    elif area_rank <= 50:
        area_comment = f"**{area}** 상권 내에서는 상위 **{area_rank:.1f}%** 로 중간 수준의 경쟁력을 보입니다."
    else:
        area_comment = f"**{area}** 상권 내에서는 상위 **{area_rank:.1f}%** 로 지역 내 경쟁력 강화가 필요합니다."
    
    # 운영 지표 분석
    if sales_section <= 2:
        sales_operation = f"매출 규모는 **상위 구간({7-sales_section:.0f}/6)** 🔥에 속해 안정적인 매출 기반을 갖추고 있습니다."
    elif sales_section <= 4:
        sales_operation = f"매출 규모는 **중간 구간({7-sales_section:.0f}/6)**으로, 프로모션과 신메뉴 출시로 매출 증대를 꾀할 수 있습니다."
    else:
        sales_operation = f"매출 규모는 **하위 구간({7-sales_section:.0f}/6)** 📈으로, 고객 유입 확대를 위한 적극적인 마케팅이 필요합니다."

    if price_section <= 2:
        price_operation = f"객단가는 **상위 구간({7-price_section:.0f}/6)** 💰으로 프리미엄 포지셔닝에 성공했습니다."
    elif price_section <= 4:
        price_operation = f"객단가는 **중간 구간({7-price_section:.0f}/6)**으로, 추가 메뉴 제안이나 세트 구성으로 상향 가능성이 있습니다."
    else:
        price_operation = f"객단가는 **하위 구간({7-price_section:.0f}/6)**으로, 사이드 메뉴 강화나 번들링 전략이 필요합니다."

    if cancel_section <= 2:
        cancel_operation = f"취소율은 **낮은 수준({7-cancel_section:.0f}/6)** ✅으로 운영이 안정적입니다."
    elif cancel_section <= 4:
        cancel_operation = f"취소율은 **보통 수준({7-cancel_section:.0f}/6)**으로, 주문 확인 프로세스 개선을 고려해볼 만합니다."
    else:
        cancel_operation = f"취소율은 **높은 수준({7-cancel_section:.0f}/6)** ⚠️으로, 메뉴 정확도와 배달 시간 관리에 주의가 필요합니다."

    # 고객 구성 분석
    retention_pct = f"{retention:.1f}%"
    new_cust_pct = f"{new_cust:.1f}%"
    residential_pct = f"{residential:.1f}%"
    office_pct = f"{office:.1f}%"
    floating_pct = f"{floating:.1f}%"

    if retention > 60:
        retention_analysis = f"재방문 고객 비중이 <b>{retention_pct}</b> 💎로 <b>매우 높아</b> 고객 충성도가 탄탄합니다."
        retention_suggestion = "현재의 서비스 품질을 유지하면서 VIP 프로그램 도입을 검토하세요."
    elif retention > 40:
        retention_analysis = f"재방문 고객 비중이 <b>{retention_pct}</b>로 양호한 편입니다."
        retention_suggestion = "멤버십 혜택이나 쿠폰 제공으로 충성도를 더욱 높일 수 있습니다."
    else:
        retention_analysis = f"재방문 고객 비중이 <b>{retention_pct}</b> 📈로 <b>낮은 편</b>이어서 고객 이탈이 우려됩니다."
        retention_suggestion = "재방문 유도 프로그램(적립, 할인쿠폰)을 시급히 도입해야 합니다."

    if new_cust > 50:
        new_cust_analysis = f"신규 고객 비중은 <b>{new_cust_pct}</b> 🌱로 <b>높아</b> 시장 확장이 활발합니다."
        new_cust_suggestion = "이들을 단골로 전환시키는 것이 다음 과제입니다."
    elif new_cust > 30:
        new_cust_analysis = f"신규 고객 비중은 <b>{new_cust_pct}</b>로 적정 수준입니다."
        new_cust_suggestion = ""
    else:
        new_cust_analysis = f"신규 고객 비중은 <b>{new_cust_pct}</b>로 낮아 성장 동력이 약합니다."
        new_cust_suggestion = "SNS 마케팅이나 제휴 프로모션으로 신규 유입을 늘려야 합니다."

    # 고객 유형별 전략
    dominant_type = max([('거주', residential), ('직장', office), ('유동', floating)], key=lambda x: x[1])
    if dominant_type[0] == '거주' and dominant_type[1] > 40:
        customer_type_analysis = f"<b>거주 고객</b> 비중이 <b>{residential_pct}</b>로 가장 높아 지역 주민 중심의 안정적인 고객층을 확보했습니다."
        customer_type_suggestion = "지역 커뮤니티와의 연계 강화(동네 행사 협찬 등)가 효과적입니다."
    elif dominant_type[0] == '직장' and dominant_type[1] > 40:
        customer_type_analysis = f"<b>직장 고객</b> 비중이 <b>{office_pct}</b>로 가장 높아 업무 지구의 특성을 잘 활용하고 있습니다."
        customer_type_suggestion = "평일 점심/저녁 시간대 회전율 향상과 테이크아웃 편의성 개선에 집중하세요."
    elif dominant_type[0] == '유동' and dominant_type[1] > 40:
        customer_type_analysis = f"<b>유동인구</b> 비중이 <b>{floating_pct}</b>로 가장 높아 일회성 고객 의존도가 높습니다."
        customer_type_suggestion = "재방문 유도 장치(쿠폰, SNS 팔로우 혜택)를 마련해 고정 고객으로 전환하는 전략이 필수입니다."
    else:
        customer_type_analysis = f"거주({residential_pct}), 직장({office_pct}), 유동({floating_pct})이 <b>고르게 분포</b>되어 있습니다."
        customer_type_suggestion = "다양한 고객층을 만족시키는 균형 잡힌 메뉴 구성이 중요합니다."

    interpretation = f"""
    ##### 📊 **{store_name}** 종합 분석 리포트
    ##### 🏆 업종/상권 내 경쟁력 지표 분석

    **{store_name}**은 **{industry}** 업종과 비교했을 때, 
    {sales_comment}

    {rank_comment} {rank_suggestion}

    {area_comment}

    > 💡 **종합 제언**: {"업종 내 입지가 탄탄하므로 현재 전략을 유지하면서 세부 최적화에 집중하세요." if industry_rank <= 30 else "경쟁력 강화를 위해 **가격 경쟁력**, **메뉴 차별화**, **고객 서비스 개선** 중 우선순위를 정해 집중 투자가 필요합니다." if industry_rank <= 50 else "⚠️ **긴급 개선 필요** - 벤치마킹을 통한 전면적인 사업 전략 재수립을 권장합니다."}

    ##### 📊 운영 지표 분석

    {sales_operation} 
    {price_operation} 
    {cancel_operation}

    > 💡 **운영 제언**: {"현재 운영 효율이 우수하므로 품질 유지에 집중하세요." if sales_section <= 2 and cancel_section <= 3 else "매출 증대를 위해 **피크타임 운영 최적화**와 **메뉴 구성 재검토**를 고려하세요." if sales_section > 2 else "취소율 관리를 위해 **주문 프로세스 점검**과 **배달 파트너 교육**이 필요합니다." if cancel_section > 4 else "안정적인 운영을 유지하고 있습니다."}


    ##### 👥 고객 구성 분석

    {retention_analysis} {retention_suggestion}
    {new_cust_analysis} {new_cust_suggestion}
    {customer_type_analysis} {customer_type_suggestion}

    > 💡 **고객 전략 제언**: {"재방문율과 신규 유입이 모두 양호하여 성장 기반이 탄탄합니다. 현재 방향을 유지하세요." if retention > 50 and new_cust > 30 else "재방문율 개선이 최우선 과제입니다. **멤버십 프로그램** 도입을 적극 검토하세요." if retention < 40 else "신규 고객 유입 확대를 위한 **마케팅 투자**가 필요합니다." if new_cust < 30 else "균형 잡힌 성장을 이어가고 있습니다."}

    ---

    **📌 비교 기준**: {comparison_label}  
    **📈 차트 해석**: 파란선(우리 매장)이 회색선(평균)보다 바깥쪽에 있을수록 해당 지표가 우수함을 의미합니다.
    """
    
    return charts, insight_text, comparison_label, interpretation




def create_customer_segment_pie(df, store_id):
    """고객 세그먼트 파이 차트 (남녀 비중 툴팁 추가)"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None
    
    recent_data = store_data.sort_values('기준년월').iloc[-1]
    
    # 연령대별 데이터
    age_data = {
        '20대↓': {
            '남성': recent_data.get('남성 20대이하 고객 비중', 0),
            '여성': recent_data.get('여성 20대이하 고객 비중', 0)
        },
        '30대': {
            '남성': recent_data.get('남성 30대 고객 비중', 0),
            '여성': recent_data.get('여성 30대 고객 비중', 0)
        },
        '40대': {
            '남성': recent_data.get('남성 40대 고객 비중', 0),
            '여성': recent_data.get('여성 40대 고객 비중', 0)
        },
        '50대': {
            '남성': recent_data.get('남성 50대 고객 비중', 0),
            '여성': recent_data.get('여성 50대 고객 비중', 0)
        },
        '60대↑': {
            '남성': recent_data.get('남성 60대이상 고객 비중', 0),
            '여성': recent_data.get('여성 60대이상 고객 비중', 0)
        }
    }
    
    labels = []
    values = []
    hover_texts = []
    
    for age, gender_data in age_data.items():
        total = gender_data['남성'] + gender_data['여성']
        labels.append(age)
        values.append(total)
        
        male_pct = (gender_data['남성'] / total * 100) if total > 0 else 0
        female_pct = (gender_data['여성'] / total * 100) if total > 0 else 0
        
        hover_text = f"<b>{age}</b><br>" \
                    f"전체: {total:.1f}%<br>" \
                    f"남성: {gender_data['남성']:.1f}% ({male_pct:.0f}%)<br>" \
                    f"여성: {gender_data['여성']:.1f}% ({female_pct:.0f}%)"
        hover_texts.append(hover_text)
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']),
        textinfo='label+percent',
        textfont_size=12,
        hovertext=hover_texts,
        hoverinfo='text'
    )])
    
    fig.update_layout(
        title='<b>고객 연령대 분포</b>',
        height=350,
        margin=dict(t=40, b=40, l=40, r=40),
        showlegend=False
    )
    
    return fig

def create_customer_type_pie(df, store_id):
    """고객 유형 파이 차트 + 인사이트"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None, None
    
    recent_data = store_data.sort_values('기준년월').iloc[-1]
    
    customer_types = {
        '거주 고객': recent_data.get('거주 이용 고객 비율', 0),
        '직장 고객': recent_data.get('직장 이용 고객 비율', 0),
        '유동인구': recent_data.get('유동인구 이용 고객 비율', 0)
    }
    
    # 인사이트 생성
    max_type = max(customer_types, key=customer_types.get)
    max_value = customer_types[max_type]
    
    # 고객 유형별 특성 분석
    insights = []
    
    if customer_types['거주 고객'] > 50:
        insights.append("**거주 고객 중심형** - 지역 주민 충성도가 높음. 멤버십/정기 프로모션 효과적")
    elif customer_types['직장 고객'] > 50:
        insights.append("**직장 고객 중심형** - 평일 점심/저녁 시간대 집중. 테이크아웃/배달 강화 필요")
    elif customer_types['유동인구'] > 50:
        insights.append("**유동인구 중심형** - 일회성 고객 많음. 재방문 유도 전략 필수")
    else:
        insights.append(f"**균형형** - {max_type}이 {max_value:.1f}%로 가장 높으나 고르게 분포")
    
    # 추가 인사이트
    if customer_types['유동인구'] > 30:
        insights.append("⚠️ 유동인구 비중이 높아 날씨/계절 영향을 많이 받을 수 있음")
    
    if customer_types['거주 고객'] < 20 and customer_types['직장 고객'] < 20:
        insights.append("💡 거주/직장 고객 비중이 낮음. SNS 마케팅으로 지역 인지도 제고 필요")
    
    fig = go.Figure(data=[go.Pie(
        labels=list(customer_types.keys()),
        values=list(customer_types.values()),
        marker=dict(colors=["#78FB71", "#66B0FF", "#FFA172"]),
        hole=0.4,  # 도넛 차트
        textinfo='label+percent',
        textfont=dict(size=13),
        hovertemplate='<b>%{label}</b><br>비율: %{value:.1f}%<br>(%{percent})<extra></extra>'
    )])
    
    fig.update_layout(
        title='<b>고객 유형별 구성</b>',
        height=350,
        margin=dict(t=40, b=40, l=20, r=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        annotations=[dict(
            text=f'<b>{max_type}</b><br>{max_value:.1f}%',
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False
        )]
    )
    
    # 인사이트 텍스트
    insight_text = "\n\n".join(insights)
    
    return fig, insight_text


def create_retention_chart(df, store_id):
    """재방문/신규 고객 추이 (전월 대비 변화율 포함)"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None
    
    store_data = store_data.sort_values('기준년월')
    
    # 전월 대비 변화율 계산
    store_data['재방문_변화'] = store_data['재방문 고객 비중'].diff()
    store_data['신규_변화'] = store_data['신규 고객 비중'].diff()
    
    fig = go.Figure()
    
    # 재방문 고객
    fig.add_trace(go.Scatter(
        x=store_data['기준년월'],
        y=store_data['재방문 고객 비중'],
        mode='lines+markers',
        name='재방문',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=7),
        customdata=store_data[['재방문_변화']],
        hovertemplate='<b>재방문 고객</b><br>' +
                      '%{x|%Y-%m}<br>' +
                      '비중: %{y:.1f}%<br>' +
                      '전월 대비: %{customdata[0]:+.1f}%p<br>' +
                      '<extra></extra>'
    ))
    
    # 신규 고객
    fig.add_trace(go.Scatter(
        x=store_data['기준년월'],
        y=store_data['신규 고객 비중'],
        mode='lines+markers',
        name='신규',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=7),
        customdata=store_data[['신규_변화']],
        hovertemplate='<b>신규 고객</b><br>' +
                      '%{x|%Y-%m}<br>' +
                      '비중: %{y:.1f}%<br>' +
                      '전월 대비: %{customdata[0]:+.1f}%p<br>' +
                      '<extra></extra>'
    ))
    
    # 최근 달 강조
    if len(store_data) > 0:
        last_point = store_data.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last_point['기준년월']],
            y=[last_point['재방문 고객 비중']],
            mode='markers',
            name='최근(재방문)',
            marker=dict(size=12, color='#2ca02c', symbol='star'),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=[last_point['기준년월']],
            y=[last_point['신규 고객 비중']],
            mode='markers',
            name='최근(신규)',
            marker=dict(size=12, color='#ff7f0e', symbol='star'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title='<b>재방문/신규 고객 비중</b>',
        xaxis_title='기준년월',
        yaxis_title='비중 (%)',
        hovermode='x unified',
        height=350,
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig
def create_flow_analysis_dashboard(flow_df, district_code, store_info):
    """유동인구 종합 분석 대시보드"""
    district_data = flow_df[flow_df['행정동코드'] == district_code].copy()
    
    if district_data.empty:
        return None, None, None
    
    # 1. 시간대별 총 유동인구 + 피크타임 강조
    fig1 = create_flow_by_time_enhanced(district_data)
    
    # 2. 시간대별 연령대 분포
    fig2 = create_flow_age_distribution(district_data)
    
    # 3. 시간대별 성별 비율
    fig3 = create_flow_gender_ratio(district_data)
    
    return fig1, fig2, fig3

def create_flow_by_time_enhanced(district_data):
    """시간대별 유동인구 (피크타임 강조)"""
    time_avg = district_data.groupby('시간대구분')['총생활인구수'].mean().reset_index()
    time_avg = time_avg.sort_values('시간대구분')
    
    # 피크타임 판단 (상위 30%)
    threshold = time_avg['총생활인구수'].quantile(0.7)
    time_avg['is_peak'] = time_avg['총생활인구수'] >= threshold
    
    colors = ['#ff7f0e' if peak else '#1f77b4' for peak in time_avg['is_peak']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=time_avg['시간대구분'],
        y=time_avg['총생활인구수'],
        marker_color=colors,
        text=time_avg['총생활인구수'].apply(lambda x: f'{x:,.0f}'),
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>시간대 %{x}</b><br>' +
                      '평균 유동인구: %{y:,.0f}명<br>' +
                      '<extra></extra>'
    ))
    
    # 평균선 추가
    avg_flow = time_avg['총생활인구수'].mean()
    fig.add_hline(
        y=avg_flow,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"평균: {avg_flow:,.0f}명",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='<b>시간대별 평균 유동인구 (오렌지: 피크타임)</b>',
        xaxis_title='시간대',
        yaxis_title='평균 유동인구 (명)',
        height=350,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    return fig

def create_flow_age_distribution(district_data):
    """시간대별 연령대 유동인구 분포"""
    # 연령대별 컬럼 그룹화
    age_groups = {
        '10대↓': ['남자0세부터9세생활인구수', '남자10세부터14세생활인구수', 
                  '여자0세부터9세생활인구수', '여자10세부터14세생활인구수'],
        '10대': ['남자15세부터19세생활인구수', '여자15세부터19세생활인구수'],
        '20대': ['남자20세부터24세생활인구수', '남자25세부터29세생활인구수',
                '여자20세부터24세생활인구수', '여자25세부터29세생활인구수'],
        '30대': ['남자30세부터34세생활인구수', '남자35세부터39세생활인구수',
                '여자30세부터34세생활인구수', '여자35세부터39세생활인구수'],
        '40대': ['남자40세부터44세생활인구수', '남자45세부터49세생활인구수',
                '여자40세부터44세생활인구수', '여자45세부터49세생활인구수'],
        '50대': ['남자50세부터54세생활인구수', '남자55세부터59세생활인구수',
                '여자50세부터54세생활인구수', '여자55세부터59세생활인구수'],
        '60대↑': ['남자60세부터64세생활인구수', '남자65세부터69세생활인구수', '남자70세이상생활인구수',
                 '여자60세부터64세생활인구수', '여자65세부터69세생활인구수', '여자70세이상생활인구수']
    }
    
    # 시간대별 연령대 집계
    time_age_data = []
    for time in district_data['시간대구분'].unique():
        time_data = district_data[district_data['시간대구분'] == time]
        for age_group, cols in age_groups.items():
            total = sum([time_data[col].mean() for col in cols if col in time_data.columns])
            time_age_data.append({
                '시간대': time,
                '연령대': age_group,
                '인구수': total
            })
    
    time_age_df = pd.DataFrame(time_age_data)
    
    fig = go.Figure()
    
    colors = ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69']
    
    for idx, age_group in enumerate(age_groups.keys()):
        data = time_age_df[time_age_df['연령대'] == age_group].sort_values('시간대')
        fig.add_trace(go.Scatter(
            x=data['시간대'],
            y=data['인구수'],
            mode='lines',
            name=age_group,
            line=dict(width=2.5),
            stackgroup='one',
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         '시간대: %{x}<br>' +
                         '인구수: %{y:,.0f}명<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title='<b>시간대별 연령대 유동인구 분포</b>',
        xaxis_title='시간대',
        yaxis_title='유동인구 (명)',
        height=350,
        margin=dict(t=40, b=40, l=40, r=40),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
    )
    
    return fig

def create_flow_gender_ratio(district_data):
    """시간대별 성별 유동인구 비율"""
    # 남성/여성 컬럼 합계
    male_cols = [col for col in district_data.columns if col.startswith('남자') and '생활인구수' in col]
    female_cols = [col for col in district_data.columns if col.startswith('여자') and '생활인구수' in col]
    
    time_gender = []
    for time in sorted(district_data['시간대구분'].unique()):
        time_data = district_data[district_data['시간대구분'] == time]
        male_total = sum([time_data[col].mean() for col in male_cols])
        female_total = sum([time_data[col].mean() for col in female_cols])
        total = male_total + female_total
        
        if total > 0:
            time_gender.append({
                '시간대': time,
                '남성': male_total,
                '여성': female_total,
                '남성비율': male_total / total * 100,
                '여성비율': female_total / total * 100
            })
    
    gender_df = pd.DataFrame(time_gender)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=gender_df['시간대'],
        y=gender_df['남성'],
        name='남성',
        marker_color='#4169E1',
        hovertemplate='<b>남성</b><br>' +
                     '시간대: %{x}<br>' +
                     '인구수: %{y:,.0f}명<br>' +
                     '비율: %{customdata:.1f}%<br>' +
                     '<extra></extra>',
        customdata=gender_df['남성비율']
    ))
    
    fig.add_trace(go.Bar(
        x=gender_df['시간대'],
        y=gender_df['여성'],
        name='여성',
        marker_color='#FF69B4',
        hovertemplate='<b>여성</b><br>' +
                     '시간대: %{x}<br>' +
                     '인구수: %{y:,.0f}명<br>' +
                     '비율: %{customdata:.1f}%<br>' +
                     '<extra></extra>',
        customdata=gender_df['여성비율']
    ))
    
    fig.update_layout(
        title='<b>시간대별 성별 유동인구</b>',
        xaxis_title='시간대',
        yaxis_title='유동인구 (명)',
        barmode='stack',
        height=350,
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def analyze_flow_insights(flow_df, district_code, store_info):
    """유동인구 기반 인사이트 분석"""
    district_data = flow_df[flow_df['행정동코드'] == district_code].copy()
    
    if district_data.empty:
        return []
    
    insights = []
    
    # 1. 피크타임 분석
    time_avg = district_data.groupby('시간대구분')['총생활인구수'].mean()
    peak_time = time_avg.idxmax()
    peak_value = time_avg.max()
    off_time = time_avg.idxmin()
    
    insights.append({
        'type': 'peak',
        'message': f"📍 피크타임: {peak_time}시 (평균 {peak_value:,.0f}명)",
        'value': peak_value,
        'time': peak_time
    })
    
    # 2. 주요 연령대 분석
    age_cols_20s = ['남자20세부터24세생활인구수', '남자25세부터29세생활인구수',
                    '여자20세부터24세생활인구수', '여자25세부터29세생활인구수']
    age_cols_30s = ['남자30세부터34세생활인구수', '남자35세부터39세생활인구수',
                    '여자30세부터34세생활인구수', '여자35세부터39세생활인구수']
    age_cols_40s = ['남자40세부터44세생활인구수', '남자45세부터49세생활인구수',
                    '여자40세부터44세생활인구수', '여자45세부터49세생활인구수']
    
    total_20s = sum([district_data[col].mean() for col in age_cols_20s if col in district_data.columns])
    total_30s = sum([district_data[col].mean() for col in age_cols_30s if col in district_data.columns])
    total_40s = sum([district_data[col].mean() for col in age_cols_40s if col in district_data.columns])
    total_flow = district_data['총생활인구수'].mean()
    
    age_ratios = {
        '20대': (total_20s / total_flow * 100) if total_flow > 0 else 0,
        '30대': (total_30s / total_flow * 100) if total_flow > 0 else 0,
        '40대': (total_40s / total_flow * 100) if total_flow > 0 else 0
    }
    
    dominant_age = max(age_ratios, key=age_ratios.get)
    insights.append({
        'type': 'age',
        'message': f"👥 주요 유동인구: {dominant_age} ({age_ratios[dominant_age]:.1f}%)",
        'value': age_ratios[dominant_age],
        'age_group': dominant_age
    })
    
    # 3. 성별 분석
    male_cols = [col for col in district_data.columns if col.startswith('남자') and '생활인구수' in col]
    female_cols = [col for col in district_data.columns if col.startswith('여자') and '생활인구수' in col]
    
    male_total = sum([district_data[col].mean() for col in male_cols])
    female_total = sum([district_data[col].mean() for col in female_cols])
    
    if male_total + female_total > 0:
        male_ratio = male_total / (male_total + female_total) * 100
        dominant_gender = "남성" if male_ratio > 50 else "여성"
        dominant_ratio = max(male_ratio, 100 - male_ratio)
        
        insights.append({
            'type': 'gender',
            'message': f"⚖️ 성별 비중: {dominant_gender} 우세 ({dominant_ratio:.1f}%)",
            'value': dominant_ratio,
            'gender': dominant_gender
        })
    
    # 4. 시간대 변동성 분석
    time_std = time_avg.std()
    time_mean = time_avg.mean()
    cv = (time_std / time_mean * 100) if time_mean > 0 else 0
    
    if cv > 30:
        insights.append({
            'type': 'volatility',
            'message': f"⚠️ 시간대별 유동인구 변동이 큼 (변동계수: {cv:.1f}%)",
            'value': cv,
            'recommendation': "피크타임 집중 마케팅 권장"
        })
    
    return insights


def create_delivery_ratio_chart(df, store_id):
    """배달매출 비율 추이 (전월 대비 변화율 포함)"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None
    
    store_data = store_data.sort_values('기준년월')
    
    # 전월 대비 변화율 계산
    store_data['배달_변화'] = store_data['배달매출금액 비율'].diff()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=store_data['기준년월'],
        y=store_data['배달매출금액 비율'],
        mode='lines+markers',
        name='배달매출 비율',
        line=dict(color='#9467bd', width=3),
        marker=dict(size=7),
        fill='tozeroy',
        fillcolor='rgba(148, 103, 189, 0.3)',
        customdata=store_data[['배달_변화']],
        hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                      '배달 비율: %{y:.1f}%<br>' +
                      '전월 대비: %{customdata[0]:+.1f}%p<br>' +
                      '<extra></extra>'
    ))
    
    # 최근 달 강조
    if len(store_data) > 0:
        last_point = store_data.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last_point['기준년월']],
            y=[last_point['배달매출금액 비율']],
            mode='markers',
            name='최근 데이터',
            marker=dict(size=15, color='#ff7f0e', symbol='star'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    fig.update_layout(
        title='<b>배달매출 비율 추이</b>',
        xaxis_title='기준년월',
        yaxis_title='비율 (%)',
        hovermode='x unified',
        height=350,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    return fig

def create_competitive_position(df, store_id):
    """경쟁 포지션 분석 (직관적인 바 차트 + 해석)"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None, None
    
    recent_data = store_data.sort_values('기준년월').iloc[-1]
    
    categories = ['업종 내 매출 순위', '상권 내 매출 순위']
    values = [
        recent_data.get('동일 업종 내 매출 순위 비율', 0),
        recent_data.get('동일 상권 내 매출 순위 비율', 0)
    ]
    
    # 평균값 계산
    avg_industry = df['동일 업종 내 매출 순위 비율'].mean()
    avg_area = df['동일 상권 내 매출 순위 비율'].mean()

    # 색상 및 평가 텍스트
    def get_evaluation(value):
        if value <= 30:
            return '우수', "#78FB71", '상위 30% 이내'  # 소프트 그린
        elif value <= 50:
            return '보통', "#FFA172", '상위 50% 이내'  # 소프트 오렌지
        else:
            return '개선 필요', "#FF7E7E", '하위 50%'  # 소프트 핑크
    
    eval_industry = get_evaluation(values[0])
    eval_area = get_evaluation(values[1])
    
    colors = [eval_industry[1], eval_area[1]]
    
    fig = go.Figure()
    
    # 가맹점 순위 바
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        name='현재 가맹점',
        marker=dict(color=colors, line=dict(color='white', width=2)),
        text=[f'{v:.1f}%<br>({get_evaluation(v)[0]})' for v in values],
        textposition='outside',
        textfont=dict(size=12, color='black'),
        hovertemplate=(
            '<b>%{x}</b><br>'
            '순위 비율: %{y:.1f}%<br>'
            '<b>해석:</b> %{customdata[0]}<br>'
            '평균 대비: %{customdata[1]}<br>'
            '<extra></extra>'
        ),
        customdata=[
            [eval_industry[2], f'{values[0] - avg_industry:+.1f}%p'],
            [eval_area[2], f'{values[1] - avg_area:+.1f}%p']
        ]
    ))
    
    # 평균선 (반투명 바)
    fig.add_trace(go.Bar(
        x=categories,
        y=[avg_industry, avg_area],
        name='전체 평균',
        marker=dict(color='lightgray', opacity=0.5, line=dict(color='gray', width=1)),
        text=[f'평균: {avg_industry:.1f}%', f'평균: {avg_area:.1f}%'],
        textposition='inside',
        hovertemplate='<b>전체 평균</b><br>%{y:.1f}%<extra></extra>'
    ))
    
    # 기준선
    fig.add_hline(
        y=50, 
        line_dash="dash", 
        line_color="rgba(255,0,0,0.3)", 
        annotation_text="중위값 (50%)",
        annotation_position="right",
        annotation_font=dict(size=10, color="red")
    )
    
    fig.update_layout(
        title='<b>경쟁 포지션 분석</b><br><sub>※ 순위 비율이 낮을수록 경쟁력이 우수함</sub>',
        xaxis_title='',
        yaxis_title='순위 비율 (%)',
        yaxis_range=[0, 100],
        height=350,
        margin=dict(t=60, b=40, l=40, r=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        barmode='group'
    )
    
    # 해석 텍스트 생성
    interpretation = f"""
    **📊 경쟁력 분석 결과**
    
    - **업종 내 순위**: {values[0]:.1f}% → {eval_industry[0]} ({eval_industry[2]})
      - 전체 평균({avg_industry:.1f}%) 대비 {values[0] - avg_industry:+.1f}%p
    
    - **상권 내 순위**: {values[1]:.1f}% → {eval_area[0]} ({eval_area[2]})
      - 전체 평균({avg_area:.1f}%) 대비 {values[1] - avg_area:+.1f}%p
    
    💡 **해석 가이드**
    - 순위 비율 30% 이하: 상위권 (우수)
    - 순위 비율 30~50%: 중위권 (보통)
    - 순위 비율 50% 초과: 하위권 (개선 필요)
    """
    
    return fig, interpretation



def create_gender_comparison(df, store_id):
    """성별 고객 비교"""
    store_data = df[df['가맹점구분번호'] == store_id].copy()
    
    if store_data.empty:
        return None
    
    recent_data = store_data.sort_values('기준년월').iloc[-1]
    
    male_total = sum([
        recent_data.get('남성 20대이하 고객 비중', 0),
        recent_data.get('남성 30대 고객 비중', 0),
        recent_data.get('남성 40대 고객 비중', 0),
        recent_data.get('남성 50대 고객 비중', 0),
        recent_data.get('남성 60대이상 고객 비중', 0)
    ])
    
    female_total = sum([
        recent_data.get('여성 20대이하 고객 비중', 0),
        recent_data.get('여성 30대 고객 비중', 0),
        recent_data.get('여성 40대 고객 비중', 0),
        recent_data.get('여성 50대 고객 비중', 0),
        recent_data.get('여성 60대이상 고객 비중', 0)
    ])
    
    fig = go.Figure(data=[go.Pie(
        labels=['남성', '여성'],
        values=[male_total, female_total],
        hole=0.5,
        marker=dict(colors=['#4169E1', '#FF69B4']),
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title='<b>성별 고객 비율</b>',
        height=350,
        margin=dict(t=40, b=40, l=40, r=40),
        showlegend=False
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="마케팅 대시보드",
        page_icon="📊",
        layout="wide"
    )
    
    # 데이터 로드
    with st.spinner('데이터 로딩 중...'):
        flow_df, rent_df, integrated_df = load_data()
    
    if integrated_df is None:
        st.error("❌ 데이터를 불러올 수 없습니다. CSV 파일 경로를 확인하세요.")
        return
    
    # 헤더
    st.markdown("""
        <h1 style='text-align: center; color: #1f77b4;'>📊 마케팅 대시보드</h1>
        <p style='text-align: center; color: #666; font-size: 18px;'>가맹점 데이터 기반 종합 분석 시스템</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 가맹점 및 분석 기간 설정
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # 가맹점 선택
        available_stores = integrated_df['가맹점구분번호'].dropna().unique()
        
        if len(available_stores) == 0:
            st.error("❌ 유효한 가맹점 데이터가 없습니다.")
            return
        
        selected_store = st.selectbox(
            "🏪 가맹점",
            options=available_stores,
            index=0,
            help="분석할 가맹점과 분석기간을 선택하세요"
        )
        
        # 분석 기간 선택
        available_months = sorted(integrated_df['기준년월'].dropna().unique())
        
        if len(available_months) > 0:
            # 포맷 변환 함수
            def format_month(x):
                if isinstance(x, pd.Timestamp):
                    return x.strftime('%Y-%m')
                else:
                    x_str = str(int(x))
                    return f"{x_str[:4]}-{x_str[4:]}"
            
            date_col1, date_col2 = st.columns(2)
            
            with date_col1:
                start_month = st.selectbox(
                    "📅 시작 월",
                    options=available_months,
                    index=0,  # 전체 기간의 첫 달을 디폴트로
                    format_func=format_month
                )
            
            with date_col2:
                end_month = st.selectbox(
                    "📅 종료 월",
                    options=available_months,
                    index=len(available_months) - 1,  # 전체 기간의 마지막 달을 디폴트로
                    format_func=format_month
                )
            
            # 선택된 기간으로 데이터 필터링
            integrated_df = integrated_df[
                (integrated_df['기준년월'] >= start_month) &
                (integrated_df['기준년월'] <= end_month)
            ]
            
            st.info(f"📊 분석 기간: {format_month(start_month)} ~ {format_month(end_month)} ({len(integrated_df):,}건)")
        else:
            st.warning("날짜 데이터가 없습니다.")

    if not selected_store:
        st.warning("⚠️ 가맹점을 선택하세요.")
        return

    # 선택된 가맹점 데이터
    store_data = integrated_df[integrated_df['가맹점구분번호'] == selected_store]

    if store_data.empty:
        st.error(f"❌ 선택한 가맹점의 선택된 기간 데이터가 없습니다.")
        return

    store_info = store_data.iloc[0]
    store_data_sorted = store_data.sort_values('기준년월')
    recent_data = store_data_sorted.iloc[-1]

    # 전월 데이터 (있는 경우)
    prev_data = store_data_sorted.iloc[-2] if len(store_data_sorted) >= 2 else None


    st.markdown("---")
    
    # 가맹점 정보 헤더
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    with info_col1:
        st.markdown(f"""
            <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #1f77b4;'>
                <h4 style='margin: 0; color: #1f77b4;'>📍 가맹점명</h4>
                <p style='margin: 5px 0 0 0; font-size: 16px;'>{store_info.get('가맹점명', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown(f"""
            <div style='background-color: #f0fff0; padding: 15px; border-radius: 10px; border-left: 5px solid #2ca02c;'>
                <h4 style='margin: 0; color: #2ca02c;'>🏢 업종</h4>
                <p style='margin: 5px 0 0 0; font-size: 16px;'>{store_info.get('업종', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with info_col3:
        st.markdown(f"""
            <div style='background-color: #fff5ee; padding: 15px; border-radius: 10px; border-left: 5px solid #ff7f0e;'>
                <h4 style='margin: 0; color: #ff7f0e;'>📍 상권</h4>
                <p style='margin: 5px 0 0 0; font-size: 16px;'>{store_info.get('상권') if pd.notna(store_info.get('상권')) else 'N/A'}</p>
            </div>
        """, unsafe_allow_html=True)

    with info_col4:
        open_date = store_info.get('개설일', 'N/A')
        
        # 날짜 포맷 변환
        if pd.notna(open_date) and open_date != 'N/A':
            try:
                date_str = str(int(open_date))  # 20220225.0 -> 20220225
                if len(date_str) == 8:
                    year = date_str[:4]
                    month = date_str[4:6]
                    day = date_str[6:8]
                    open_date_display = f"{year}년 {month}월 {day}일"
                else:
                    open_date_display = str(open_date)
            except:
                open_date_display = 'N/A'
        else:
            open_date_display = 'N/A'
        
        st.markdown(f"""
            <div style='background-color: #fff0f5; padding: 15px; border-radius: 10px; border-left: 5px solid #d62728;'>
                <h4 style='margin: 0; color: #d62728;'>📅 개설일</h4>
                <p style='margin: 5px 0 0 0; font-size: 16px;'>{open_date_display}</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI 메트릭 (5개 - 전월 대비 추가)
    st.markdown("#### 📈 핵심 성과 지표 (KPI)")
    # kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.metric("💰 매출금액 구간", recent_data.get('매출금액 구간', 'N/A'))
    
    with kpi_col2:
        st.metric("🛒 매출건수 구간", recent_data.get('매출건수 구간', 'N/A'))
    
    with kpi_col3:
        st.metric("👥 유니크 고객 수", recent_data.get('유니크 고객 수 구간', 'N/A'))
    
    with kpi_col4:
        st.metric("💵 객단가 구간", recent_data.get('객단가 구간', 'N/A'))
    
    st.markdown("---")
    
    # 메인 대시보드
    st.markdown("### 📊 종합 비즈니스 분석")

    # 종합 평가 (상단에 가로로 길게)
    radar_fig, radar_summary, radar_explanations = create_business_strength_radar(integrated_df, selected_store)

    if radar_fig:
        st.markdown(radar_summary, unsafe_allow_html=True)
    else:
        st.info("📊 종합 평가 데이터를 불러올 수 없습니다.")
        
    # Row 1: 3개 컬럼으로 구성
    col1, col2, col3 = st.columns([1.5,2,1.5])

    # 왼쪽: 비즈니스 강점 레이더 + 종합 평가
    with col1:
        st.markdown("#### 💼 비즈니스 강점 분석")
        
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)
            
            with st.expander("📖 지표 산출 기준 보기"):
                for metric_name, explanation in radar_explanations.items():
                    st.markdown(f"##### {metric_name}")
                    st.markdown(explanation)
        else:
            st.warning("비즈니스 지표 데이터가 없습니다")
        

    # 중간: 상세 레이더 차트 (탭)
    with col2:
        st.markdown("#### 📊 상세 지표 분석")
        charts, radar_insights, comparison_name, radar_interpretation = create_sales_trend_comparison(integrated_df, selected_store)

        if charts:
            tab_names = [chart[0] for chart in charts]
            tabs = st.tabs(tab_names)
            
            for tab, (title, chart) in zip(tabs, charts):
                with tab:
                    st.plotly_chart(chart, use_container_width=True)
            
            with st.expander("📖 상세 해석 보기"):
                st.markdown(radar_interpretation, unsafe_allow_html=True)
        else:
            st.warning("레이더 차트 데이터가 없습니다")

    # 오른쪽: 경쟁 포지션만
    with col3:
        st.markdown("#### 🏆 경쟁 포지션")
        competitive_fig, competitive_interpretation = create_competitive_position(integrated_df, selected_store)
        
        if competitive_fig:
            st.plotly_chart(competitive_fig, use_container_width=True)
            
            with st.expander("📖 해석 보기"):
                st.markdown(competitive_interpretation)
        else:
            st.warning("경쟁 포지션 데이터 없음")
        
    # Row 2
    st.markdown("---")
    st.markdown("#### 👥 고객 분석")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_age = create_customer_segment_pie(integrated_df, selected_store)
        if fig_age:
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("연령대 데이터 없음")
    
    with col2:
        fig_gender = create_gender_comparison(integrated_df, selected_store)
        if fig_gender:
            st.plotly_chart(fig_gender, use_container_width=True)
        else:
            st.info("성별 데이터 없음")
    
    with col3:
        customer_fig, customer_insight = create_customer_type_pie(integrated_df, selected_store)
        if customer_fig:
            st.plotly_chart(customer_fig, use_container_width=True)
            
            with st.expander("💡 인사이트 보기"):
                st.markdown(customer_insight)
        else:
            st.warning("고객 유형 데이터가 없음")
    
    # Row 3
    st.markdown("---")
    st.markdown("#### 🔄 재방문 분석 & 유동인구")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig_retention = create_retention_chart(integrated_df, selected_store)
        if fig_retention:
            st.plotly_chart(fig_retention, use_container_width=True)
        else:
            st.info("재방문 데이터 없음")
    
    with col2:
        if flow_df is not None:
            district_code = get_store_district_code(store_info, flow_df)
            if district_code:
                # 3개의 유동인구 시각화
                fig_flow1, fig_flow2, fig_flow3 = create_flow_analysis_dashboard(
                    flow_df, district_code, store_info
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if fig_flow1:
                        st.plotly_chart(fig_flow1, use_container_width=True, key="sales_trend")

                with col2:
                    if fig_flow2:
                        st.plotly_chart(fig_flow2, use_container_width=True, key="delivery_ratio")

                with col3:
                    if fig_flow3:
                        st.plotly_chart(fig_flow3, use_container_width=True, key="competitive_position")
                
                # 유동인구 인사이트 분석
                flow_insights = analyze_flow_insights(flow_df, district_code, store_info)
                
            else:
                st.info("행정동 매칭 실패")
        else:
            st.info("유동인구 데이터 없음")
    
    st.markdown("---")
    
    # 인사이트
    st.markdown("## 💡 주요 인사이트")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.markdown("#### ✅ 강점")
        retention_rate = recent_data.get('재방문 고객 비중', 0)
        if retention_rate > 60:
            st.success(f"✅ 높은 재방문율: {retention_rate:.1f}%")
        
        delivery_ratio = recent_data.get('배달매출금액 비율', 0)
        if delivery_ratio > 30:
            st.success(f"✅ 안정적 배달 매출: {delivery_ratio:.1f}%")
        
        rank_industry = recent_data.get('동일 업종 내 매출 순위 비율', 0)
        if rank_industry <= 30:
            st.success(f"✅ 업종 내 상위권: {rank_industry:.1f}%")
    
    with insight_col2:
        st.markdown("#### ⚠️ 주의사항")
        if retention_rate < 40:
            st.warning(f"⚠️ 재방문율 낮음: {retention_rate:.1f}%")
        
        new_customer = recent_data.get('신규 고객 비중', 0)
        if new_customer < 25:
            st.warning(f"⚠️ 신규 고객 유입 부족: {new_customer:.1f}%")
        
        if rank_industry > 70:
            st.warning(f"⚠️ 업종 내 하위권: {rank_industry:.1f}%")
    
    with insight_col3:
        st.markdown("#### 🎯 제안사항")
        
        # 재방문율 기반 제안
        if retention_rate < 50:
            st.info(f"📌 **재방문 촉진 전략 필요**\n"
                    f"- 근거: 현재 재방문율 {retention_rate:.1f}%로 업계 평균 대비 낮은 수준\n"
                    f"- 제안: 멤버십/쿠폰 프로그램 도입으로 고객 충성도 제고")
        
        # 신규 고객 비율 기반 제안
        if new_customer < 30:
            st.info(f"📌 **신규 고객 유입 강화 필요**\n"
                    f"- 근거: 신규 고객 비율 {new_customer:.1f}%로 성장 동력 부족\n"
                    f"- 제안: SNS 광고 및 지역 제휴 마케팅 통해 신규 고객층 확대")
        
        flow_usage = recent_data.get('유동인구 이용 고객 비율', 0)

        # 유동인구 기반 제안
        if flow_df is not None and district_code:
            flow_insights = analyze_flow_insights(flow_df, district_code, store_info)
            for insight in flow_insights:
                if insight['type'] == 'peak':
                    peak_time = insight['time']
                    st.info(f"📌 **피크타임 집중 운영 전략**\n"
                            f"- 근거: 유동인구 데이터 분석 결과 {peak_time}시 유동량 최대\n"
                            f"- 제안: {peak_time}시 전후 해피아워/타임특가 프로모션 운영")
                elif insight['type'] == 'age':
                    age_group = insight['age_group']
                    st.info(f"📌 **타겟 연령층 맞춤 마케팅**\n"
                            f"- 근거: 상권 유동인구 중 {age_group} 비중 가장 높음\n"
                            f"- 제안: {age_group} 선호 메뉴 개발 및 SNS 채널 집중 공략")
                elif insight['type'] == 'volatility' and 'recommendation' in insight:
                    st.info(f"📌 **유동인구 변동성 대응**\n"
                            f"- 근거: {insight.get('reason', '유동인구 패턴 분석')}\n"
                            f"- 제안: {insight['recommendation']}")
                
if __name__ == "__main__":
    main()