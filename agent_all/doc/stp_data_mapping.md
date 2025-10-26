# STP 검증을 위한 데이터 매핑 정의서

## 📋 목차
1. [데이터 소스 정의](#1-데이터-소스-정의)
2. [S (Segmentation) 검증 데이터](#2-s-segmentation-검증-데이터)
3. [T (Targeting) 검증 데이터](#3-t-targeting-검증-데이터)
4. [P (Positioning) 검증 데이터](#4-p-positioning-검증-데이터)
5. [통계 분석 데이터](#5-통계-분석-데이터)
6. [데이터 모델 설계](#6-데이터-모델-설계)

---

## 1. 데이터 소스 정의

### 1.1 주요 데이터셋

| 파일명 | 약칭 | 주요 용도 | 키 |
|-------|-----|---------|---|
| `big_data_set2_f_re.csv` | **DS2** | 가맹점 월별 이용정보 (매출, 운영) | 가맹점구분번호 |
| `big_data_set3_f_re.csv` | **DS3** | 가맹점 월별 고객정보 (인구통계) | 가맹점구분번호 |
| `df_final.csv` | **DF** | 가맹점 최종 데이터 (경쟁, 리스크) | 가맹점구분번호 |
| `store_segmentation_final_re.csv` | **SS** | 가맹점 포지셔닝 (PCA, Cluster) | 가맹점구분번호 |
| `상권_feature.csv` | **CF** | 상권별 통계 | 상권 |
| `pca_components_by_industry.csv` | **PCA** | PCA 가중치 | 업종 |
| `kmeans_clusters_by_industry.csv` | **KM** | 클러스터 프로파일 | 업종 |

### 1.2 컬럼명 매핑 (원본 → 영문)

#### DS2 (big_data_set2_f_re.csv)
```python
DS2_COLUMN_MAPPING = {
    '가맹점 운영개월수 구간': 'operation_months_bin',
    '매출금액 구간': 'sales_amount_bin',
    '매출건수 구간': 'sales_count_bin',
    '유니크 고객 수 구간': 'unique_customer_bin',
    '객단가 구간': 'avg_price_bin',
    '취소율 구간': 'cancel_rate_bin',
    '배달매출금액 비율': 'delivery_sales_ratio',  # DLV_SAA_RAT
    '동일 업종 매출금액 비율': 'same_industry_sales_ratio',
    '동일 업종 매출건수 비율': 'same_industry_count_ratio',
    '동일 업종 내 매출 순위 비율': 'industry_sales_rank_pct',
    '동일 상권 내 매출 순위 비율': 'area_sales_rank_pct',
    '동일 업종 내 배치 가맹점 비중': 'industry_closed_ratio',
    '동일 상권 내 배치 가맹점 비중': 'area_closed_ratio'
}
```

#### DS3 (big_data_set3_f_re.csv)
```python
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
```

#### DF (df_final.csv) - 이미 영문
```python
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
```

---

## 2. S (Segmentation) 검증 데이터

### 2.1 목적
**"우리 가맹점이 속한 시장 군집이 실제 고객 데이터와 일치하는가?"**

### 2.2 필요 데이터

| 검증 항목 | 데이터 소스 | 컬럼명 | 용도 |
|----------|-----------|--------|------|
| **고객 연령/성별 분포** | DS3 | male_20s_ratio ~ female_60s_ratio | 타겟 고객층 검증 |
| **고객 유형 분포** | DS3 | resident_customer_ratio<br>worker_customer_ratio<br>floating_customer_ratio | 주 고객 유형 (거주/직장/유동) |
| **재방문율** | DS3 | revisit_ratio | 충성도 검증 |
| **신규 고객율** | DS3 | new_customer_ratio | 성장 가능성 |
| **상권 고객 다양성** | CF | 상권_고객다양성 | 시장 포용성 |
| **업종 다양성** | CF | 상권_업종다양성 | 경쟁 구도 |

### 2.3 검증 로직

```python
def validate_segmentation(
    cluster_profile: ClusterProfile,  # 분석팀에서 생성한 군집 프로파일
    store_customer_data: Dict  # DS3에서 추출한 실제 고객 데이터
) -> SegmentationValidation:
    """
    클러스터의 특성과 실제 고객 데이터 일치 여부 검증
    
    예시:
    - 클러스터명: "2030 직장인 중심"
    - 검증: male_20s + male_30s + female_20s + female_30s ≥ 50%
    - 검증: worker_customer_ratio ≥ 40%
    """
    
    # 1. 연령대 분포 검증
    age_20_30_ratio = (
        store_customer_data['male_20s_ratio'] +
        store_customer_data['male_30s_ratio'] +
        store_customer_data['female_20s_ratio'] +
        store_customer_data['female_30s_ratio']
    )
    
    # 2. 고객 유형 검증
    worker_ratio = store_customer_data['worker_customer_ratio']
    
    # 3. 재방문율 검증
    revisit_ratio = store_customer_data['revisit_ratio']
    
    validation_result = {
        'age_match': age_20_30_ratio >= 50.0,
        'age_ratio': age_20_30_ratio,
        'customer_type_match': worker_ratio >= 40.0,
        'worker_ratio': worker_ratio,
        'loyalty_level': 'high' if revisit_ratio >= 40.0 else 'medium' if revisit_ratio >= 25.0 else 'low',
        'overall_match_score': calculate_match_score(...)
    }
    
    return validation_result
```

---

## 3. T (Targeting) 검증 데이터

### 3.1 목적
**"선정한 타겟 군집이 수익성/성장성/안정성 측면에서 타당한가?"**

### 3.2 필요 데이터

| 검증 차원 | 데이터 소스 | 컬럼명 | 판단 기준 |
|----------|-----------|--------|----------|
| **🔵 수익성** | | | |
| - 매출 규모 | DS2 | sales_amount_bin | 상위 50% 이상 |
| - 업종 대비 매출 | DS2 | same_industry_sales_ratio | 1.0 이상 |
| - 상권 내 순위 | DS2 | area_sales_rank_pct | 상위 30% |
| - 객단가 | DS2 | avg_price_bin | 중간 이상 |
| **🟢 성장성** | | | |
| - 매출 증감률 | DF | Δsales_4w | 양수 (0 이상) |
| - 신규 고객 비율 | DS3 | new_customer_ratio | 10% 이상 |
| - 상권 매출 증감률 | CF | 상권_매출증감률 | 음수가 아님 |
| **🟡 안정성** | | | |
| - 리스크 점수 | DF | risk_score_xgb | 0.3 이하 |
| - 매출 변동성 | DF | sales_volatility_4w | 낮을수록 좋음 |
| - 경쟁 강도 | DF | comp_intensity | 적정 수준 |
| - 평균 생존 개월수 | DF | avg_survival_months | 높을수록 좋음 |
| - 재방문율 | DS3 | revisit_ratio | 30% 이상 |

### 3.3 검증 로직

```python
def validate_targeting(
    target_cluster_id: int,
    store_performance_data: Dict,  # DF + DS2
    store_customer_data: Dict       # DS3
) -> TargetingValidation:
    """
    타겟 군집의 비즈니스 타당성 검증
    """
    
    # 1. 수익성 점수 (0~100)
    profitability_score = calculate_profitability_score(
        sales_ratio=store_performance_data['same_industry_sales_ratio'],
        sales_rank=store_performance_data['area_sales_rank_pct'],
        avg_price_bin=store_performance_data['avg_price_bin']
    )
    
    # 2. 성장성 점수 (0~100)
    growth_score = calculate_growth_score(
        sales_growth=store_performance_data['Δsales_4w'],
        new_customer_ratio=store_customer_data['new_customer_ratio']
    )
    
    # 3. 안정성 점수 (0~100)
    stability_score = calculate_stability_score(
        risk_score=store_performance_data['risk_score_xgb'],
        volatility=store_performance_data['sales_volatility_4w'],
        revisit_ratio=store_customer_data['revisit_ratio']
    )
    
    # 4. 종합 판단
    overall_score = (
        profitability_score * 0.4 +
        growth_score * 0.3 +
        stability_score * 0.3
    )
    
    return {
        'profitability_score': profitability_score,
        'growth_score': growth_score,
        'stability_score': stability_score,
        'overall_score': overall_score,
        'recommendation': 'strong' if overall_score >= 70 else 'moderate' if overall_score >= 50 else 'weak',
        'reasoning': generate_reasoning(...)
    }
```

---

## 4. P (Positioning) 검증 데이터

### 4.1 목적
**"추천된 White Space 포지션이 실제 운영 가능한가?"**

### 4.2 필요 데이터

| 검증 항목 | 데이터 소스 | 컬럼명 | 전략 연결 |
|----------|-----------|--------|----------|
| **🎨 Product 전략 검증** | | | |
| - 배달 매출 비율 | DS2 | delivery_sales_ratio | Place 전략에 직접 반영 |
| - 객단가 | DS2 | avg_price_bin | Price 전략에 직접 반영 |
| - 재방문율 | DS3 | revisit_ratio | 제품 만족도 추정 |
| **💰 Price 전략 검증** | | | |
| - 현재 객단가 | DS2 | avg_price_bin | 가격 책정 기준 |
| - PC1 좌표 | SS | pc1_x | 가격 포지셔닝 |
| - 업종 평균 매출 | DS2 | same_industry_sales_ratio | 가격 경쟁력 |
| **📍 Place 전략 검증** | | | |
| - 배달 매출 비중 | DS2 | delivery_sales_ratio | 배달/매장 비중 결정 |
| - 유동인구 고객 비율 | DS3 | floating_customer_ratio | 입지 중요도 |
| - 직장 고객 비율 | DS3 | worker_customer_ratio | 상권 특성 |
| **📢 Promotion 전략 검증** | | | |
| - 신규 고객 비율 | DS3 | new_customer_ratio | 신규 유입 전략 |
| - 재방문율 | DS3 | revisit_ratio | 충성도 프로그램 |
| - 주 고객층 연령대 | DS3 | male_20s_ratio ~ female_60s_ratio | 타겟 광고 채널 |
| - 고객 유형 | DS3 | resident/worker/floating | 프로모션 시간대 |

### 4.3 검증 로직

```python
def validate_positioning_for_4p(
    white_space: WhiteSpace,  # 추천된 빈 포지션
    store_operational_data: Dict,  # DS2
    store_customer_data: Dict       # DS3
) -> PositioningValidation:
    """
    White Space 포지션의 실현 가능성 및 4P 전략 구체화
    """
    
    # 1. Product 전략 데이터
    product_insights = {
        'delivery_focused': store_operational_data['delivery_sales_ratio'] > 50.0,
        'delivery_ratio': store_operational_data['delivery_sales_ratio'],
        'customer_satisfaction': store_customer_data['revisit_ratio']
    }
    
    # 2. Price 전략 데이터
    price_insights = {
        'current_price_level': extract_price_from_bin(
            store_operational_data['avg_price_bin']
        ),
        'pc1_coord': white_space.pc1_coord,  # 고가/저가 포지셔닝
        'price_competitiveness': store_operational_data['same_industry_sales_ratio']
    }
    
    # 3. Place 전략 데이터
    place_insights = {
        'channel_strategy': {
            'delivery': store_operational_data['delivery_sales_ratio'],
            'dine_in': 100 - store_operational_data['delivery_sales_ratio']
        },
        'customer_type': {
            'resident': store_customer_data['resident_customer_ratio'],
            'worker': store_customer_data['worker_customer_ratio'],
            'floating': store_customer_data['floating_customer_ratio']
        },
        'recommended_focus': determine_channel_focus(...)
    }
    
    # 4. Promotion 전략 데이터
    promotion_insights = {
        'target_age_groups': extract_top_age_groups(store_customer_data),
        'acquisition_vs_retention': {
            'new_ratio': store_customer_data['new_customer_ratio'],
            'revisit_ratio': store_customer_data['revisit_ratio']
        },
        'promotion_timing': determine_timing_from_customer_type(
            store_customer_data['worker_customer_ratio']
        )
    }
    
    return {
        'product_data': product_insights,
        'price_data': price_insights,
        'place_data': place_insights,
        'promotion_data': promotion_insights,
        'feasibility_score': calculate_feasibility(...),
        'recommendation': generate_4p_recommendation(...)
    }
```

---

## 5. 통계 분석 데이터

### 5.1 advanced_statistical_analysis 활용

#### 기존 통계 분석 Output
```python
advanced_statistical_analysis(data_dict, target_store_id) 반환값:
{
    '1_기초통계': {...},
    '2_매출분석': {...},
    '3_상권분석': {
        '집중도_지표': {
            '상위10_비중': float,
            '허핀달지수': float
        },
        '경쟁도_분석': {...}
    },
    '4_업종분석': {...},
    '5_위험도분석': {
        'risk_level': str,  # 'low', 'medium', 'high'
        '고위험_비율': float
    },
    '6_경쟁강도분석': {...},
    '7_고객분석': {...},
    '8_이상치분석': {...},
    '9_target_store_analysis': {
        '가맹점구분번호': str,
        '가맹점명': str,
        '전체_비교': {...},
        '상권_비교': {...}
    }
}
```

### 5.2 Strategy Agent에서 활용

```python
def enrich_stp_with_statistics(
    stp_output: STPOutput,
    stats_analysis: Dict
) -> EnrichedSTPOutput:
    """
    통계 분석 결과를 STP에 통합
    """
    
    # 1. Segmentation에 통계 추가
    market_concentration = stats_analysis['3_상권분석']['집중도_지표']
    
    # 2. Targeting에 위험도 추가
    risk_analysis = stats_analysis['5_위험도분석']
    
    # 3. Positioning에 경쟁 강도 추가
    competition_analysis = stats_analysis['6_경쟁강도분석']
    
    return {
        'stp_output': stp_output,
        'statistics': {
            'market_concentration': market_concentration,
            'risk_level': risk_analysis['risk_level'],
            'competition_intensity': competition_analysis
        }
    }
```

---

## 6. 데이터 모델 설계

### 6.1 Pydantic 모델 정의

```python
from pydantic import BaseModel, Field
from typing import Dict, Optional

# ========================================
# 1. Segmentation 검증 모델
# ========================================

class CustomerDemographics(BaseModel):
    """고객 인구통계 데이터"""
    male_20s_ratio: float
    male_30s_ratio: float
    male_40s_ratio: float
    male_50s_ratio: float
    male_60s_ratio: float
    female_20s_ratio: float
    female_30s_ratio: float
    female_40s_ratio: float
    female_50s_ratio: float
    female_60s_ratio: float
    
    def get_age_20_30_ratio(self) -> float:
        """20-30대 비율 계산"""
        return (
            self.male_20s_ratio + self.male_30s_ratio +
            self.female_20s_ratio + self.female_30s_ratio
        )
    
    def get_dominant_age_group(self) -> str:
        """주요 연령대 판단"""
        age_groups = {
            '20대': self.male_20s_ratio + self.female_20s_ratio,
            '30대': self.male_30s_ratio + self.female_30s_ratio,
            '40대': self.male_40s_ratio + self.female_40s_ratio,
            '50대': self.male_50s_ratio + self.female_50s_ratio,
            '60대+': self.male_60s_ratio + self.female_60s_ratio
        }
        return max(age_groups, key=age_groups.get)

class CustomerTypeDistribution(BaseModel):
    """고객 유형 분포"""
    resident_ratio: float = Field(description="거주 이용 고객")
    worker_ratio: float = Field(description="직장 이용 고객")
    floating_ratio: float = Field(description="유동인구 고객")
    
    def get_dominant_type(self) -> str:
        """주 고객 유형"""
        types = {
            'resident': self.resident_ratio,
            'worker': self.worker_ratio,
            'floating': self.floating_ratio
        }
        return max(types, key=types.get)

class CustomerLoyalty(BaseModel):
    """고객 충성도"""
    revisit_ratio: float = Field(description="재방문 고객 비율")
    new_customer_ratio: float = Field(description="신규 고객 비율")
    
    def get_loyalty_level(self) -> str:
        """충성도 등급"""
        if self.revisit_ratio >= 40.0:
            return 'high'
        elif self.revisit_ratio >= 25.0:
            return 'medium'
        else:
            return 'low'

class SegmentationData(BaseModel):
    """Segmentation 검증용 데이터"""
    demographics: CustomerDemographics
    customer_type: CustomerTypeDistribution
    loyalty: CustomerLoyalty

# ========================================
# 2. Targeting 검증 모델
# ========================================

class ProfitabilityMetrics(BaseModel):
    """수익성 지표"""
    sales_amount_bin: str = Field(description="매출금액 구간")
    same_industry_sales_ratio: float = Field(description="업종 대비 매출 비율")
    area_sales_rank_pct: float = Field(description="상권 내 매출 순위 백분위")
    avg_price_bin: str = Field(description="객단가 구간")
    
    def get_profitability_score(self) -> float:
        """수익성 점수 (0~100)"""
        # 구간 점수 변환
        sales_score = extract_score_from_bin(self.sales_amount_bin)
        
        # 업종 대비 점수 (1.0 기준)
        ratio_score = min(self.same_industry_sales_ratio * 100, 100)
        
        # 순위 점수 (백분위 그대로)
        rank_score = self.area_sales_rank_pct
        
        # 객단가 점수
        price_score = extract_score_from_bin(self.avg_price_bin)
        
        return (sales_score * 0.3 + ratio_score * 0.3 + 
                rank_score * 0.2 + price_score * 0.2)

class GrowthMetrics(BaseModel):
    """성장성 지표"""
    delta_sales_4w: float = Field(description="4주 매출 증감률")
    new_customer_ratio: float = Field(description="신규 고객 비율")
    market_sales_growth: float = Field(description="상권 매출 증감률")
    
    def get_growth_score(self) -> float:
        """성장성 점수 (0~100)"""
        # 매출 증감률 점수
        sales_growth_score = normalize_to_100(self.delta_sales_4w, -0.2, 0.2)
        
        # 신규 고객 점수
        new_cust_score = min(self.new_customer_ratio * 5, 100)
        
        return sales_growth_score * 0.6 + new_cust_score * 0.4

class StabilityMetrics(BaseModel):
    """안정성 지표"""
    risk_score_xgb: float = Field(description="XGBoost 리스크 점수")
    sales_volatility_4w: float = Field(description="매출 변동성")
    comp_intensity: float = Field(description="경쟁 강도")
    avg_survival_months: float = Field(description="평균 생존 개월수")
    revisit_ratio: float = Field(description="재방문율")
    
    def get_stability_score(self) -> float:
        """안정성 점수 (0~100)"""
        # 리스크 점수 (0~1, 낮을수록 좋음)
        risk_score = (1 - self.risk_score_xgb) * 100
        
        # 변동성 점수 (낮을수록 좋음)
        volatility_score = normalize_to_100(self.sales_volatility_4w, 0.1, 0.01)
        
        # 생존 점수
        survival_score = normalize_to_100(self.avg_survival_months, 200, 800)
        
        # 재방문율 점수
        revisit_score = min(self.revisit_ratio * 2, 100)
        
        return (risk_score * 0.3 + volatility_score * 0.2 + 
                survival_score * 0.2 + revisit_score * 0.3)

class TargetingData(BaseModel):
    """Targeting 검증용 데이터"""
    profitability: ProfitabilityMetrics
    growth: GrowthMetrics
    stability: StabilityMetrics

# ========================================
# 3. Positioning 검증 모델
# ========================================

class ProductStrategyData(BaseModel):
    """Product 전략 데이터"""
    delivery_sales_ratio: float = Field(description="배달 매출 비율")
    revisit_ratio: float = Field(description="재방문율 (제품 만족도)")
    
    def is_delivery_focused(self) -> bool:
        return self.delivery_sales_ratio > 50.0

class PriceStrategyData(BaseModel):
    """Price 전략 데이터"""
    avg_price_bin: str = Field(description="객단가 구간")
    pc1_coord: float = Field(description="PC1 좌표 (가격 포지셔닝)")
    same_industry_sales_ratio: float = Field(description="업종 대비 매출")
    
    def get_price_level(self) -> str:
        """가격 수준"""
        if self.pc1_coord > 1.0:
            return 'premium'
        elif self.pc1_coord > -1.0:
            return 'mid-range'
        else:
            return 'budget'

class PlaceStrategyData(BaseModel):
    """Place 전략 데이터"""
    delivery_ratio: float
    dine_in_ratio: float
    customer_type_dist: CustomerTypeDistribution
    
    def get_recommended_channel_mix(self) -> Dict[str, float]:
        """추천 채널 믹스"""
        if self.delivery_ratio > 60:
            return {'delivery': 70, 'dine_in': 30}
        elif self.delivery_ratio > 40:
            return {'delivery': 50, 'dine_in': 50}
        else:
            return {'delivery': 30, 'dine_in': 70}

class PromotionStrategyData(BaseModel):
    """Promotion 전략 데이터"""
    target_age_groups: list[str]
    new_customer_ratio: float
    revisit_ratio: float
    customer_type_dist: CustomerTypeDistribution
    
    def get_promotion_focus(self) -> str:
        """프로모션 초점"""
        if self.new_customer_ratio < 10.0 and self.revisit_ratio > 35.0:
            return 'retention'  # 유지 중심
        elif self.new_customer_ratio > 15.0:
            return 'acquisition'  # 유치 중심
        else:
            return 'balanced'  # 균형

class PositioningData(BaseModel):
    """Positioning 검증용 데이터 (4P 연결)"""
    product: ProductStrategyData
    price: PriceStrategyData
    place: PlaceStrategyData
    promotion: PromotionStrategyData

# ========================================
# 4. 통합 데이터 모델
# ========================================

class StoreRawData(BaseModel):
    """가맹점 실제 데이터 (통합)"""
    # 식별 정보
    store_id: str
    store_name: str
    industry: str
    commercial_area: str
    
    # Segmentation 데이터
    segmentation: SegmentationData
    
    # Targeting 데이터
    targeting: TargetingData
    
    # Positioning 데이터
    positioning: PositioningData
    
    # 추가 메타데이터
    operation_months: int
    base_month: str = Field(description="기준년월 (YYYYMM)")

# ========================================
# 5. 검증 결과 모델
# ========================================

class SegmentationValidation(BaseModel):
    """Segmentation 검증 결과"""
    cluster_name: str
    age_match: bool
    age_20_30_ratio: float
    customer_type_match: bool
    dominant_customer_type: str
    loyalty_level: str
    match_score: float = Field(description="0~100")
    reasoning: str

class TargetingValidation(BaseModel):
    """Targeting 검증 결과"""
    profitability_score: float = Field(description="수익성 점수 0~100")
    growth_score: float = Field(description="성장성 점수 0~100")
    stability_score: float = Field(description="안정성 점수 0~100")
    overall_score: float = Field(description="종합 점수 0~100")
    recommendation: str = Field(description="strong/moderate/weak")
    reasoning: str

class PositioningValidation(BaseModel):
    """Positioning 검증 결과 (4P 구체화)"""
    product_insights: Dict
    price_insights: Dict
    place_insights: Dict
    promotion_insights: Dict
    feasibility_score: float = Field(description="실현 가능성 0~100")
    recommendation: str
```

---

## 7. 데이터 추출 함수 설계

### 7.1 StoreDataEnricher 클래스

```python
class StoreDataEnricher:
    """가맹점 실제 데이터 추출 및 변환"""
    
    def __init__(self, data_dir: str):
        self.df_ds2 = pd.read_csv(f"{data_dir}/big_data_set2_f_re.csv", encoding='utf-8')
        self.df_ds3 = pd.read_csv(f"{data_dir}/big_data_set3_f_re.csv", encoding='utf-8')
        self.df_final = pd.read_csv(f"{data_dir}/df_final.csv", encoding='cp949')
        self.df_commercial = pd.read_csv(f"{data_dir}/상권_feature.csv", encoding='utf-8')
        
    def get_store_raw_data(
        self,
        store_id: str,
        base_month: str = '202404'
    ) -> StoreRawData:
        """가맹점 ID로 통합 데이터 추출"""
        
        # 1. 기본 정보
        store_basic = self._get_store_basic_info(store_id)
        
        # 2. Segmentation 데이터
        segmentation_data = self._extract_segmentation_data(store_id, base_month)
        
        # 3. Targeting 데이터
        targeting_data = self._extract_targeting_data(store_id, base_month)
        
        # 4. Positioning 데이터
        positioning_data = self._extract_positioning_data(store_id, base_month)
        
        return StoreRawData(
            store_id=store_id,
            store_name=store_basic['store_name'],
            industry=store_basic['industry'],
            commercial_area=store_basic['commercial_area'],
            segmentation=segmentation_data,
            targeting=targeting_data,
            positioning=positioning_data,
            operation_months=store_basic['operation_months'],
            base_month=base_month
        )
    
    def _extract_segmentation_data(
        self,
        store_id: str,
        base_month: str
    ) -> SegmentationData:
        """DS3에서 Segmentation 데이터 추출"""
        
        df = self.df_ds3[
            (self.df_ds3['가맹점구분번호'] == store_id) &
            (self.df_ds3['기준년월'] == int(base_month))
        ]
        
        if df.empty:
            # 최신 월 데이터 사용
            df = self.df_ds3[self.df_ds3['가맹점구분번호'] == store_id].sort_values('기준년월', ascending=False).head(1)
        
        row = df.iloc[0]
        
        # 결측치 처리 (-999999.9 → 0.0)
        def clean_value(val):
            return 0.0 if val == -999999.9 or pd.isna(val) else float(val)
        
        return SegmentationData(
            demographics=CustomerDemographics(
                male_20s_ratio=clean_value(row['남성 20대이하 고객 비중']),
                male_30s_ratio=clean_value(row['남성 30대 고객 비중']),
                male_40s_ratio=clean_value(row['남성 40대 고객 비중']),
                male_50s_ratio=clean_value(row['남성 50대 고객 비중']),
                male_60s_ratio=clean_value(row['남성 60대이상 고객 비중']),
                female_20s_ratio=clean_value(row['여성 20대이하 고객 비중']),
                female_30s_ratio=clean_value(row['여성 30대 고객 비중']),
                female_40s_ratio=clean_value(row['여성 40대 고객 비중']),
                female_50s_ratio=clean_value(row['여성 50대 고객 비중']),
                female_60s_ratio=clean_value(row['여성 60대이상 고객 비중'])
            ),
            customer_type=CustomerTypeDistribution(
                resident_ratio=clean_value(row['거주 이용 고객 비율']),
                worker_ratio=clean_value(row['직장 이용 고객 비율']),
                floating_ratio=clean_value(row['유동인구 이용 고객 비율'])
            ),
            loyalty=CustomerLoyalty(
                revisit_ratio=clean_value(row['재방문 고객 비중']),
                new_customer_ratio=clean_value(row['신규 고객 비중'])
            )
        )
    
    def _extract_targeting_data(...):
        """DS2 + DF에서 Targeting 데이터 추출"""
        # 유사하게 구현
        ...
    
    def _extract_positioning_data(...):
        """DS2 + DS3에서 Positioning 데이터 추출"""
        # 유사하게 구현
        ...
```

---

## 8. Strategy Agent 통합 예시

```python
def strategy_agent_node(state: StrategyTeamState) -> StrategyTeamState:
    """Strategy Agent with Data Validation"""
    
    stp = state['stp_output']
    raw_data = stp.store_raw_data  # StoreRawData 객체
    
    # ====================================
    # Step 1: Segmentation 검증
    # ====================================
    segmentation_validation = validate_segmentation_with_data(
        cluster_profile=stp.cluster_profiles[stp.target_cluster_id],
        segmentation_data=raw_data.segmentation
    )
    
    # ====================================
    # Step 2: Targeting 검증
    # ====================================
    targeting_validation = validate_targeting_with_data(
        target_cluster_id=stp.target_cluster_id,
        targeting_data=raw_data.targeting
    )
    
    # ====================================
    # Step 3: Positioning 검증 (4P 구체화)
    # ====================================
    positioning_validation = validate_positioning_for_4p(
        white_space=stp.recommended_white_space,
        positioning_data=raw_data.positioning
    )
    
    # ====================================
    # Step 4: LLM으로 통합 전략 생성
    # ====================================
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)
    
    prompt = f"""
    # STP 분석 결과
    - Segmentation: {stp.cluster_profiles}
    - Targeting: {stp.target_cluster_name}
    - Positioning: {stp.recommended_white_space}
    
    # 검증 결과
    ## Segmentation 검증
    {segmentation_validation}
    
    ## Targeting 검증
    - 수익성 점수: {targeting_validation.profitability_score}
    - 성장성 점수: {targeting_validation.growth_score}
    - 안정성 점수: {targeting_validation.stability_score}
    
    ## Positioning 검증 (4P 데이터)
    ### Product
    - 배달 중심: {raw_data.positioning.product.is_delivery_focused()}
    - 배달 비율: {raw_data.positioning.product.delivery_sales_ratio}%
    
    ### Price
    - 가격 수준: {raw_data.positioning.price.get_price_level()}
    - 객단가 구간: {raw_data.positioning.price.avg_price_bin}
    
    ### Place
    - 추천 채널 믹스: {raw_data.positioning.place.get_recommended_channel_mix()}
    - 주 고객 유형: {raw_data.positioning.place.customer_type_dist.get_dominant_type()}
    
    ### Promotion
    - 프로모션 초점: {raw_data.positioning.promotion.get_promotion_focus()}
    - 주 타겟 연령대: {raw_data.positioning.promotion.target_age_groups}
    
    ---
    
    위 데이터를 바탕으로 4P 전략을 수립하세요.
    """
    
    response = llm.invoke(prompt)
    
    # 전략 파싱 및 반환
    ...
```

---

## 요약

| STP 단계 | 주요 데이터 소스 | 핵심 컬럼 | 검증 목적 |
|---------|--------------|---------|---------|
| **S** | DS3 | 연령/성별, 고객유형, 재방문율 | 군집 특성 일치 여부 |
| **T** | DF + DS2 | 매출, 리스크, 성장률, 변동성 | 비즈니스 타당성 |
| **P** | DS2 + DS3 | 배달비율, 객단가, 고객유형 | 4P 전략 구체화 |

이 구조로 진행하면 **분석팀의 PCA/K-Means 결과**와 **가맹점 실제 데이터**가 모두 Strategy Agent에 통합되어, 데이터 기반의 실행 가능한 전략을 생성할 수 있습니다.
