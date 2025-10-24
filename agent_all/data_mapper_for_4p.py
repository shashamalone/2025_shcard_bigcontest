"""
4P 전략을 위한 데이터 매핑 모듈
가맹점 데이터를 Product, Price, Place, Promotion 전략에 맞게 매핑
"""

import pandas as pd
from typing import Dict, Optional
from pathlib import Path

DATA_DIR = "/mnt/c/Users/rladl/Desktop/bigcontest_2025/2025_shcard_bigcontest/data"

# ============================================================================
# 1. 컬럼명 매핑 정의
# ============================================================================

DS2_COLUMN_MAPPING = {
    '가맹점 운영개월수 구간': 'operation_months_bin',
    '매출금액 구간': 'sales_amount_bin',
    '매출건수 구간': 'sales_count_bin',
    '유니크 고객 수 구간': 'unique_customer_bin',
    '객단가 구간': 'avg_price_bin',
    '취소율 구간': 'cancel_rate_bin',
    '배달매출금액 비율': 'delivery_sales_ratio',
    '동일 업종 매출금액 비율': 'same_industry_sales_ratio',
    '동일 업종 매출건수 비율': 'same_industry_count_ratio',
    '동일 업종 내 매출 순위 비율': 'industry_sales_rank_pct',
    '동일 상권 내 매출 순위 비율': 'area_sales_rank_pct',
    '동일 업종 내 배치 가맹점 비중': 'industry_closed_ratio',
    '동일 상권 내 배치 가맹점 비중': 'area_closed_ratio'
}

DS3_COLUMN_MAPPING = {
    '남성 20대이하 고객 비중': 'male_20s_ratio',
    '남성 30대 고객 비중': 'male_30s_ratio',
    '남성 40대 고객 비중': 'male_40s_ratio',
    '남성 50대 고객 비중': 'male_50s_ratio',
    '남성 60대이상 고객 비중': 'male_60s_ratio',
    '여성 20대이하 고객 비중': 'female_20s_ratio',
    '여성 30대 고객 비중': 'female_30s_ratio',
    '여성 40대 고객 비중': 'female_40s_ratio',
    '여성 50대 고객 비중': 'female_50s_ratio',
    '여성 60대이상 고객 비중': 'female_60s_ratio',
    '재방문 고객 비중': 'revisit_ratio',
    '신규 고객 비중': 'new_customer_ratio',
    '거주 이용 고객 비율': 'resident_customer_ratio',
    '직장 이용 고객 비율': 'worker_customer_ratio',
    '유동인구 이용 고객 비율': 'floating_customer_ratio'
}

DF_COLUMNS = [
    'comp_intensity',           # 경쟁 강도
    'market_churn_rate_4w',     # 상권 이탈률
    'same_industry_sales_ratio', # 동일업종 매출비중
    'customer_fit_score',       # 고객 적합도
    'avg_survival_months',      # 평균 생존개월수
    'Δsales_4w',                # 매출 증감률
    'sales_volatility_4w',      # 매출 변동성
    'risk_score_xgb'            # 리스크 점수
]

# ============================================================================
# 2. 데이터 로더
# ============================================================================

class DataLoaderFor4P:
    """4P 전략용 데이터 로더"""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.ds2 = None  # 가맹점 월별 이용정보
        self.ds3 = None  # 가맹점 월별 고객정보
        self.df_final = None  # 가맹점 최종 데이터

    def load_all(self):
        """전체 데이터 로드 - 여러 인코딩 시도"""
        encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']

        try:
            # DS2: 이용정보
            for enc in encodings:
                try:
                    self.ds2 = pd.read_csv(
                        self.data_dir / "big_data_set2_f_re.csv",
                        encoding=enc
                    )
                    print(f"   DS2 로드 성공 (encoding={enc})")
                    break
                except:
                    continue

            # DS3: 고객정보
            for enc in encodings:
                try:
                    self.ds3 = pd.read_csv(
                        self.data_dir / "big_data_set3_f_re.csv",
                        encoding=enc
                    )
                    print(f"   DS3 로드 성공 (encoding={enc})")
                    break
                except:
                    continue

            # DF: 최종 데이터
            for enc in encodings:
                try:
                    self.df_final = pd.read_csv(
                        self.data_dir / "df_final.csv",
                        encoding=enc
                    )
                    print(f"   DF 로드 성공 (encoding={enc})")
                    break
                except:
                    continue

            # 로드 실패한 파일 체크
            if self.ds2 is None:
                self.ds2 = pd.DataFrame()
            if self.ds3 is None:
                self.ds3 = pd.DataFrame()
            if self.df_final is None:
                self.df_final = pd.DataFrame()

            print("✅ 4P 전략용 데이터 로드 완료")

        except Exception as e:
            print(f"⚠️  데이터 로드 실패: {e}")
            self.ds2 = pd.DataFrame()
            self.ds3 = pd.DataFrame()
            self.df_final = pd.DataFrame()

# ============================================================================
# 3. 4P 데이터 매퍼
# ============================================================================

class DataMapperFor4P:
    """4P 전략별 데이터 매핑"""

    def __init__(self, loader: DataLoaderFor4P):
        self.loader = loader

    def get_product_data(self, store_id: str) -> Dict:
        """🎨 Product 전략 데이터"""
        product_data = {
            "category": "Product (제품/서비스)",
            "data_sources": []
        }

        # DS2: 매출/운영 데이터
        if not self.loader.ds2.empty:
            ds2_row = self.loader.ds2[self.loader.ds2['가맹점구분번호'] == store_id]
            if not ds2_row.empty:
                row = ds2_row.iloc[-1]  # 최신 데이터
                product_data["data_sources"].append({
                    "source": "가맹점 운영 데이터",
                    "metrics": {
                        "배달_매출_비율": f"{row.get('배달매출금액 비율', 0):.1%}",
                        "객단가_구간": row.get('객단가 구간', 'N/A'),
                        "취소율": row.get('취소율 구간', 'N/A'),
                        "매출건수_구간": row.get('매출건수 구간', 'N/A')
                    },
                    "insights": {
                        "배달_의존도": "높음" if row.get('배달매출금액 비율', 0) > 0.5 else "중간" if row.get('배달매출금액 비율', 0) > 0.3 else "낮음",
                        "제품_만족도_추정": "양호" if row.get('취소율 구간', '') in ['매우 낮음', '낮음'] else "개선 필요"
                    }
                })

        # DS3: 고객 재방문율
        if not self.loader.ds3.empty:
            ds3_row = self.loader.ds3[self.loader.ds3['가맹점구분번호'] == store_id]
            if not ds3_row.empty:
                row = ds3_row.iloc[-1]
                revisit = row.get('재방문 고객 비중', 0)
                product_data["data_sources"].append({
                    "source": "고객 충성도 데이터",
                    "metrics": {
                        "재방문율": f"{revisit:.1%}"
                    },
                    "insights": {
                        "제품_만족도": "높음" if revisit > 0.3 else "중간" if revisit > 0.2 else "낮음",
                        "전략_방향": "재방문율이 높으므로 제품 품질 유지 및 메뉴 다양화" if revisit > 0.3 else "재방문율 개선 필요"
                    }
                })

        return product_data

    def get_price_data(self, store_id: str) -> Dict:
        """💰 Price 전략 데이터"""
        price_data = {
            "category": "Price (가격)",
            "data_sources": []
        }

        # DS2: 객단가 및 업종 대비 매출
        if not self.loader.ds2.empty:
            ds2_row = self.loader.ds2[self.loader.ds2['가맹점구분번호'] == store_id]
            if not ds2_row.empty:
                row = ds2_row.iloc[-1]
                same_industry_ratio = row.get('동일 업종 매출금액 비율', 1.0)

                price_data["data_sources"].append({
                    "source": "가격 경쟁력 데이터",
                    "metrics": {
                        "객단가_구간": row.get('객단가 구간', 'N/A'),
                        "업종_대비_매출_비율": f"{same_industry_ratio:.2f}",
                        "업종_내_매출_순위": f"상위 {row.get('동일 업종 내 매출 순위 비율', 0):.1%}",
                        "상권_내_매출_순위": f"상위 {row.get('동일 상권 내 매출 순위 비율', 0):.1%}"
                    },
                    "insights": {
                        "가격_경쟁력": "우수" if same_industry_ratio >= 1.0 else "보통" if same_industry_ratio >= 0.8 else "개선 필요",
                        "전략_방향": "프리미엄 가격 전략 가능" if same_industry_ratio >= 1.2 else "적정 가격 유지" if same_industry_ratio >= 0.9 else "가격 경쟁력 강화 필요"
                    }
                })

        # DF: 리스크 및 안정성
        if not self.loader.df_final.empty:
            df_row = self.loader.df_final[self.loader.df_final['가맹점구분번호'] == store_id]
            if not df_row.empty:
                row = df_row.iloc[0]
                sales_volatility = row.get('sales_volatility_4w', 0)

                price_data["data_sources"].append({
                    "source": "가격 안정성 데이터",
                    "metrics": {
                        "매출_변동성": f"{sales_volatility:.2f}",
                        "매출_증감률": f"{row.get('Δsales_4w', 0):.1%}"
                    },
                    "insights": {
                        "가격_안정성": "안정" if sales_volatility < 0.5 else "변동 있음",
                        "전략_방향": "가격 고정 전략" if sales_volatility < 0.3 else "유연한 가격 전략 (할인/프로모션)"
                    }
                })

        return price_data

    def get_place_data(self, store_id: str) -> Dict:
        """📍 Place 전략 데이터"""
        place_data = {
            "category": "Place (유통/채널)",
            "data_sources": []
        }

        # DS2: 배달 매출 비중
        if not self.loader.ds2.empty:
            ds2_row = self.loader.ds2[self.loader.ds2['가맹점구분번호'] == store_id]
            if not ds2_row.empty:
                row = ds2_row.iloc[-1]
                delivery_ratio = row.get('배달매출금액 비율', 0)

                place_data["data_sources"].append({
                    "source": "채널 분포 데이터",
                    "metrics": {
                        "배달_매출_비중": f"{delivery_ratio:.1%}",
                        "매장_매출_비중": f"{1 - delivery_ratio:.1%}"
                    },
                    "insights": {
                        "주력_채널": "배달" if delivery_ratio > 0.6 else "매장" if delivery_ratio < 0.3 else "혼합",
                        "전략_방향": f"배달 채널 강화 (현재 {delivery_ratio:.0%})" if delivery_ratio > 0.5 else f"매장 경험 개선 (현재 오프라인 {1-delivery_ratio:.0%})"
                    }
                })

        # DS3: 고객 유형 (거주/직장/유동)
        if not self.loader.ds3.empty:
            ds3_row = self.loader.ds3[self.loader.ds3['가맹점구분번호'] == store_id]
            if not ds3_row.empty:
                row = ds3_row.iloc[-1]
                resident = row.get('거주 이용 고객 비율', 0)
                worker = row.get('직장 이용 고객 비율', 0)
                floating = row.get('유동인구 이용 고객 비율', 0)

                main_customer_type = max(
                    [('거주민', resident), ('직장인', worker), ('유동인구', floating)],
                    key=lambda x: x[1]
                )

                place_data["data_sources"].append({
                    "source": "상권 특성 데이터",
                    "metrics": {
                        "거주_고객": f"{resident:.1%}",
                        "직장_고객": f"{worker:.1%}",
                        "유동_고객": f"{floating:.1%}"
                    },
                    "insights": {
                        "주_고객_유형": main_customer_type[0],
                        "입지_특성": "주거 상권" if resident > 0.4 else "업무 상권" if worker > 0.4 else "유동 상권" if floating > 0.4 else "복합 상권",
                        "전략_방향": "근린 편의 중심 (배달/테이크아웃)" if resident > 0.4 else "점심/회식 메뉴 강화" if worker > 0.4 else "접근성/간편식 중심"
                    }
                })

        return place_data

    def get_promotion_data(self, store_id: str) -> Dict:
        """📢 Promotion 전략 데이터"""
        promotion_data = {
            "category": "Promotion (프로모션)",
            "data_sources": []
        }

        # DS3: 신규/재방문 고객
        if not self.loader.ds3.empty:
            ds3_row = self.loader.ds3[self.loader.ds3['가맹점구분번호'] == store_id]
            if not ds3_row.empty:
                row = ds3_row.iloc[-1]
                new_customer = row.get('신규 고객 비중', 0)
                revisit = row.get('재방문 고객 비중', 0)

                promotion_data["data_sources"].append({
                    "source": "고객 유입 데이터",
                    "metrics": {
                        "신규_고객_비율": f"{new_customer:.1%}",
                        "재방문_고객_비율": f"{revisit:.1%}"
                    },
                    "insights": {
                        "주_타겟": "신규 유입" if new_customer > 0.15 else "재방문 유도",
                        "전략_방향": "신규 고객 유입 캠페인 (SNS 광고, 할인 쿠폰)" if new_customer > 0.15 else "충성도 프로그램 (적립, 재방문 혜택)"
                    }
                })

                # 주 고객 연령/성별 분석
                demographics = {
                    "남성_20대": row.get('남성 20대이하 고객 비중', 0),
                    "남성_30대": row.get('남성 30대 고객 비중', 0),
                    "남성_40대": row.get('남성 40대 고객 비중', 0),
                    "여성_20대": row.get('여성 20대이하 고객 비중', 0),
                    "여성_30대": row.get('여성 30대 고객 비중', 0),
                    "여성_40대": row.get('여성 40대 고객 비중', 0)
                }

                main_demo = max(demographics.items(), key=lambda x: x[1])

                promotion_data["data_sources"].append({
                    "source": "타겟 고객 프로파일",
                    "metrics": demographics,
                    "insights": {
                        "주_타겟_고객": main_demo[0],
                        "타겟_비중": f"{main_demo[1]:.1%}",
                        "추천_채널": self._get_promotion_channel(main_demo[0]),
                        "추천_메시지": self._get_promotion_message(main_demo[0])
                    }
                })

        # DF: 성장성 데이터
        if not self.loader.df_final.empty:
            df_row = self.loader.df_final[self.loader.df_final['가맹점구분번호'] == store_id]
            if not df_row.empty:
                row = df_row.iloc[0]
                sales_growth = row.get('Δsales_4w', 0)

                promotion_data["data_sources"].append({
                    "source": "성장 트렌드 데이터",
                    "metrics": {
                        "매출_증감률": f"{sales_growth:.1%}",
                        "경쟁_강도": f"{row.get('comp_intensity', 0):.2f}"
                    },
                    "insights": {
                        "프로모션_강도": "공격적 마케팅 필요" if sales_growth < 0 else "유지 전략" if sales_growth < 0.05 else "브랜딩 집중",
                        "전략_방향": "할인/이벤트 집중" if sales_growth < 0 else "고객 만족도 유지" if sales_growth < 0.1 else "프리미엄 이미지 구축"
                    }
                })

        return promotion_data

    def _get_promotion_channel(self, demo: str) -> str:
        """타겟 고객별 추천 채널"""
        channel_map = {
            "남성_20대": "인스타그램, 유튜브 쇼츠",
            "남성_30대": "네이버 블로그, 카카오톡 채널",
            "남성_40대": "네이버 플레이스, 지역 커뮤니티",
            "여성_20대": "인스타그램 릴스, 틱톡",
            "여성_30대": "인스타그램 피드, 블로그",
            "여성_40대": "네이버 블로그, 카카오스토리"
        }
        return channel_map.get(demo, "SNS 전반")

    def _get_promotion_message(self, demo: str) -> str:
        """타겟 고객별 추천 메시지"""
        message_map = {
            "남성_20대": "가성비, 트렌디, 빠른 배달",
            "남성_30대": "품질, 합리적 가격, 편의성",
            "남성_40대": "전통, 신뢰, 건강",
            "여성_20대": "비주얼, 포토존, 인스타 감성",
            "여성_30대": "프리미엄, 분위기, 안전",
            "여성_40대": "가족 친화, 건강, 정성"
        }
        return message_map.get(demo, "품질과 가치")

    def get_all_4p_data(self, store_id: str) -> Dict:
        """전체 4P 데이터 통합"""
        return {
            "store_id": store_id,
            "Product": self.get_product_data(store_id),
            "Price": self.get_price_data(store_id),
            "Place": self.get_place_data(store_id),
            "Promotion": self.get_promotion_data(store_id)
        }

# ============================================================================
# 4. 사용 예시
# ============================================================================

if __name__ == "__main__":
    import json

    # 데이터 로드
    loader = DataLoaderFor4P()
    loader.load_all()

    # 매퍼 생성
    mapper = DataMapperFor4P(loader)

    # 샘플 가맹점 ID
    if not loader.ds2.empty:
        sample_store_id = loader.ds2['가맹점구분번호'].iloc[0]

        # 4P 데이터 추출
        data_4p = mapper.get_all_4p_data(sample_store_id)

        # JSON 출력
        print(json.dumps(data_4p, ensure_ascii=False, indent=2))
