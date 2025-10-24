"""
STP Analyzer 테스트 코드
- PrecomputedPositioningLoader 구현
- STPAnalyzerWithPrecomputedData 테스트
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


# =====================================
# 데이터 클래스 정의
# =====================================

@dataclass
class ClusterProfile:
    """클러스터 프로파일"""
    cluster_id: int
    cluster_name: str
    store_count: int
    pc1_mean: float
    pc2_mean: float
    characteristics: str


@dataclass
class PCAxisInterpretation:
    """주성분 축 해석"""
    axis: str
    interpretation: str
    top_features: List[Dict]


@dataclass
class StorePosition:
    """가맹점 포지션"""
    store_id: str
    store_name: str
    industry: str
    pc1_score: float
    pc2_score: float
    cluster_id: int
    cluster_name: str
    competitor_count: int


# =====================================
# PrecomputedPositioningLoader 구현
# =====================================

class PrecomputedPositioningLoader:
    """사전 계산된 포지셔닝 데이터 로더"""

    def __init__(
        self,
        pca_loadings_path: str,
        cluster_profiles_path: str,
        store_positioning_path: str
    ):
        # 데이터 로드
        print(f"📂 Loading data...")
        self.pca_loadings = pd.read_csv(pca_loadings_path)
        self.cluster_profiles = pd.read_csv(cluster_profiles_path)
        self.store_positioning = pd.read_csv(store_positioning_path)

        print(f"✅ PCA Loadings: {self.pca_loadings.shape}")
        print(f"✅ Cluster Profiles: {self.cluster_profiles.shape}")
        print(f"✅ Store Positioning: {self.store_positioning.shape}")

    def get_cluster_profiles(self, industry: str) -> List[ClusterProfile]:
        """업종별 클러스터 프로파일 조회"""
        df = self.cluster_profiles[self.cluster_profiles['industry'] == industry]

        profiles = []
        for _, row in df.iterrows():
            profiles.append(ClusterProfile(
                cluster_id=row['cluster_id'],
                cluster_name=row['cluster_name'],
                store_count=row['store_count'],
                pc1_mean=row['pc1_mean'],
                pc2_mean=row['pc2_mean'],
                characteristics=row['characteristics']
            ))
        return profiles

    def get_pc_axis_interpretation(self, industry: str) -> Dict[str, PCAxisInterpretation]:
        """PC축 해석 조회"""
        df = self.pca_loadings[self.pca_loadings['industry'] == industry]

        interpretations = {}
        for axis in ['PC1', 'PC2']:
            axis_data = df[df['pc_axis'] == axis].iloc[0]

            # top_features는 JSON 형태로 저장되어 있다고 가정
            import json
            top_features = json.loads(axis_data['top_features']) if isinstance(axis_data['top_features'], str) else []

            interpretations[axis] = PCAxisInterpretation(
                axis=axis,
                interpretation=axis_data['interpretation'],
                top_features=top_features
            )

        return interpretations

    def get_competitive_landscape(self, industry: str) -> Dict:
        """경쟁 구도 분석"""
        df = self.store_positioning[self.store_positioning['업종'] == industry]

        return {
            'total_competitors': len(df),
            'avg_pc1': df['pc1_x'].mean(),
            'avg_pc2': df['pc2_y'].mean(),
            'cluster_distribution': df['cluster_id'].value_counts().to_dict()
        }

    def get_store_position(self, store_id: str) -> Optional[StorePosition]:
        """가맹점 포지션 조회"""
        df = self.store_positioning[self.store_positioning['가맹점구분번호'] == store_id]

        if df.empty:
            return None

        row = df.iloc[0]
        return StorePosition(
            store_id=row['가맹점구분번호'],
            store_name=row['가맹점명'],
            industry=row['업종'],
            pc1_score=row['pc1_x'],
            pc2_score=row['pc2_y'],
            cluster_id=row['cluster_id'],
            cluster_name=row.get('cluster_name', f"Cluster {row['cluster_id']}"),
            competitor_count=row.get('num_clusters', 0)
        )

    def find_nearby_competitors(self, store_id: str, radius: float = 1.5) -> List[Dict]:
        """근접 경쟁자 찾기"""
        position = self.get_store_position(store_id)
        if not position:
            return []

        # 같은 업종 내에서 찾기
        df = self.store_positioning[self.store_positioning['업종'] == position.industry]
        df = df[df['가맹점구분번호'] != store_id]  # 자기 자신 제외

        # 유클리드 거리 계산
        df['distance'] = np.sqrt(
            (df['pc1_x'] - position.pc1_score) ** 2 +
            (df['pc2_y'] - position.pc2_score) ** 2
        )

        # 반경 내 경쟁자 필터링
        nearby = df[df['distance'] <= radius].sort_values('distance')

        competitors = []
        for _, row in nearby.head(10).iterrows():
            competitors.append({
                'store_id': row['가맹점구분번호'],
                'store_name': row['가맹점명'],
                'cluster': row.get('cluster_name', f"Cluster {row['cluster_id']}"),
                'distance': round(row['distance'], 2)
            })

        return competitors


# =====================================
# STP Analyzer
# =====================================

class STPAnalyzerWithPrecomputedData:
    """
    STP 분석기: 사전 계산된 포지셔닝 데이터 활용
    - 시장 세분화 분석 (Segmentation)
    - 가맹점 위치 파악
    - 포지셔닝 리포트 생성 (LLM 입력용)
    """

    def __init__(self, positioning_loader: PrecomputedPositioningLoader):
        self.loader = positioning_loader

    def analyze_market_structure(self, industry: str) -> Dict:
        """시장 세분화 분석 (Segmentation)"""
        # 1. 클러스터 프로파일 조회
        clusters = self.loader.get_cluster_profiles(industry)

        # 2. PC축 해석 조회
        pc_interpretations = self.loader.get_pc_axis_interpretation(industry)

        # 3. 경쟁 구도 분석
        landscape = self.loader.get_competitive_landscape(industry)

        return {
            'industry': industry,
            'segmentation': {
                'total_segments': len(clusters),
                'segments': [
                    {
                        'id': c.cluster_id,
                        'name': c.cluster_name,
                        'size': c.store_count,
                        'percentage': round(
                            c.store_count / landscape['total_competitors'] * 100,
                            1
                        ),
                        'position': f"PC1={c.pc1_mean:.2f}, PC2={c.pc2_mean:.2f}",
                        'characteristics': c.characteristics
                    }
                    for c in clusters
                ]
            },
            'positioning_axes': {
                'PC1': {
                    'interpretation': pc_interpretations['PC1'].interpretation,
                    'top_factors': pc_interpretations['PC1'].top_features
                },
                'PC2': {
                    'interpretation': pc_interpretations['PC2'].interpretation,
                    'top_factors': pc_interpretations['PC2'].top_features
                }
            },
            'competitive_density': landscape
        }

    def locate_store(self, store_id: str) -> Dict:
        """가맹점 위치 파악"""
        # 1. 포지셔닝 조회
        position = self.loader.get_store_position(store_id)
        if not position:
            raise ValueError(f"가맹점 {store_id} 데이터 없음")

        # 2. 근접 경쟁자 조회
        competitors = self.loader.find_nearby_competitors(store_id, radius=1.5)

        # 3. 클러스터 정보 조회
        clusters = self.loader.get_cluster_profiles(position.industry)
        my_cluster = next(
            (c for c in clusters if c.cluster_id == position.cluster_id),
            None
        )

        return {
            'store_name': position.store_name,
            'industry': position.industry,
            'coordinates': {
                'PC1': position.pc1_score,
                'PC2': position.pc2_score
            },
            'cluster': {
                'id': position.cluster_id,
                'name': position.cluster_name,
                'size': position.competitor_count,
                'characteristics': my_cluster.characteristics if my_cluster else 'N/A'
            },
            'nearby_competitors': competitors
        }

    def generate_positioning_report(self, store_id: str) -> str:
        """포지셔닝 리포트 생성 (LLM 입력용)"""
        # 1. 시장 구조 분석
        position = self.loader.get_store_position(store_id)
        market = self.analyze_market_structure(position.industry)
        location = self.locate_store(store_id)

        # 2. 텍스트 리포트 생성
        report = f"""
### {position.industry} 업종 시장 구조 분석

**포지셔닝 축 해석**
- PC1 축: {market['positioning_axes']['PC1']['interpretation']}
  주요 요인: {', '.join([f"{f['속성']}({f['가중치']})" for f in market['positioning_axes']['PC1']['top_factors']])}

- PC2 축: {market['positioning_axes']['PC2']['interpretation']}
  주요 요인: {', '.join([f"{f['속성']}({f['가중치']})" for f in market['positioning_axes']['PC2']['top_factors']])}

**시장 세분화 결과**
총 {market['segmentation']['total_segments']}개 경쟁 그룹 존재:
{self._format_segments(market['segmentation']['segments'])}

**가맹점 '{position.store_name}' 현재 위치**
- 소속 그룹: {location['cluster']['name']} ({location['cluster']['size']}개 경쟁자)
- 좌표: PC1={location['coordinates']['PC1']:.2f}, PC2={location['coordinates']['PC2']:.2f}
- 그룹 특성: {location['cluster']['characteristics']}

**근접 경쟁자 (1.5 반경 내)**
{self._format_competitors(location['nearby_competitors'])}
        """
        return report.strip()

    def _format_segments(self, segments: List[Dict]) -> str:
        """세그먼트 포맷팅"""
        lines = []
        for seg in segments:
            lines.append(
                f"  {seg['id']}. {seg['name']}: {seg['size']}개 ({seg['percentage']}%) - {seg['characteristics']}"
            )
        return "\n".join(lines)

    def _format_competitors(self, competitors: List[Dict]) -> str:
        """경쟁자 목록 포맷팅"""
        if not competitors:
            return "  (근접 경쟁자 없음)"

        lines = []
        for comp in competitors:
            lines.append(
                f"  - {comp['store_name']} ({comp['cluster']}, 거리: {comp['distance']})"
            )
        return "\n".join(lines)


# =====================================
# 테스트 코드
# =====================================

def create_sample_data():
    """샘플 데이터 생성"""

    # 1. PCA Loadings (업종별 PC축 해석)
    pca_df = pd.DataFrame({
        'industry': ['커피전문점', '커피전문점', '치킨전문점', '치킨전문점'],
        'pc_axis': ['PC1', 'PC2', 'PC1', 'PC2'],
        'interpretation': [
            '매출 규모 vs 생존 기간',
            '경쟁 강도 vs 고객 적합도',
            '상권 성숙도 vs 시장 변동성',
            '고객 충성도 vs 가격 경쟁력'
        ],
        'top_features': [
            '[{"속성": "매출성장률", "가중치": 0.85}, {"속성": "생존개월", "가중치": 0.72}]',
            '[{"속성": "경쟁강도", "가중치": 0.78}, {"속성": "고객적합도", "가중치": 0.65}]',
            '[{"속성": "상권성숙도", "가중치": 0.80}, {"속성": "변동성", "가중치": 0.70}]',
            '[{"속성": "고객충성도", "가중치": 0.82}, {"속성": "가격경쟁력", "가중치": 0.68}]'
        ]
    })

    # 2. Cluster Profiles (업종별 클러스터 프로파일)
    cluster_df = pd.DataFrame({
        'industry': ['커피전문점'] * 3 + ['치킨전문점'] * 3,
        'cluster_id': [0, 1, 2, 0, 1, 2],
        'cluster_name': [
            '안정형 대형점', '성장형 중형점', '신규 소형점',
            '프랜차이즈 강자', '로컬 맛집', '위기 매장'
        ],
        'store_count': [45, 32, 23, 38, 41, 21],
        'pc1_mean': [2.1, 0.3, -1.8, 1.9, 0.1, -2.2],
        'pc2_mean': [1.5, -0.5, 0.2, -1.2, 1.8, -0.3],
        'characteristics': [
            '매출 안정, 낮은 경쟁강도',
            '빠른 성장, 중간 경쟁',
            '신규 진입, 높은 리스크',
            '브랜드 파워, 높은 매출',
            '지역 밀착, 고객 충성도 높음',
            '매출 하락, 높은 변동성'
        ]
    })

    # 3. Store Positioning (가맹점별 포지셔닝) - 한글 컬럼명 사용
    np.random.seed(42)
    store_df = pd.DataFrame({
        '가맹점구분번호': [f"STORE{i:04d}" for i in range(100)],
        '가맹점명': [f"매장{i}" for i in range(100)],
        '업종': ['커피전문점'] * 50 + ['치킨전문점'] * 50,
        'pc1_x': np.random.randn(100) * 1.5,
        'pc2_y': np.random.randn(100) * 1.5,
        'cluster_id': np.random.choice([0, 1, 2], 100),
        'num_clusters': 3
    })

    # 클러스터 이름 매핑
    cluster_name_map = {
        ('커피전문점', 0): '안정형 대형점',
        ('커피전문점', 1): '성장형 중형점',
        ('커피전문점', 2): '신규 소형점',
        ('치킨전문점', 0): '프랜차이즈 강자',
        ('치킨전문점', 1): '로컬 맛집',
        ('치킨전문점', 2): '위기 매장'
    }
    store_df['cluster_name'] = store_df.apply(
        lambda x: cluster_name_map[(x['업종'], x['cluster_id'])], axis=1
    )

    return pca_df, cluster_df, store_df


def test_stp_analyzer():
    """STP Analyzer 테스트"""

    print("=" * 60)
    print("🧪 STP Analyzer Test")
    print("=" * 60)

    # 1. 샘플 데이터 생성 및 저장
    pca_df, cluster_df, store_df = create_sample_data()

    pca_df.to_csv('data/정리/pca_components_by_industry.csv', index=False)
    cluster_df.to_csv('data/정리/kmeans_clusters_by_industry.csv', index=False)
    store_df.to_csv('data/정리/store_segmentation_final.csv', index=False)

    print("\n✅ Sample data created\n")

    # 2. Loader 초기화
    loader = PrecomputedPositioningLoader(
        pca_loadings_path='data/정리/pca_components_by_industry.csv',
        cluster_profiles_path='data/정리/kmeans_clusters_by_industry.csv',
        store_positioning_path='data/정리/store_segmentation_final.csv'
    )

    # 3. STP Analyzer 초기화
    analyzer = STPAnalyzerWithPrecomputedData(loader)

    # 4. 시장 구조 분석 테스트
    print("\n" + "=" * 60)
    print("📊 Test 1: analyze_market_structure()")
    print("=" * 60)
    market = analyzer.analyze_market_structure('커피전문점')
    print(f"✅ Industry: {market['industry']}")
    print(f"✅ Total Segments: {market['segmentation']['total_segments']}")
    for seg in market['segmentation']['segments']:
        print(f"   - {seg['name']}: {seg['size']}개 ({seg['percentage']}%)")

    # 5. 가맹점 위치 파악 테스트
    print("\n" + "=" * 60)
    print("📍 Test 2: locate_store()")
    print("=" * 60)
    location = analyzer.locate_store('STORE0001')
    print(f"✅ Store: {location['store_name']}")
    print(f"✅ Cluster: {location['cluster']['name']}")
    print(f"✅ Coordinates: PC1={location['coordinates']['PC1']:.2f}, PC2={location['coordinates']['PC2']:.2f}")
    print(f"✅ Nearby Competitors: {len(location['nearby_competitors'])}개")

    # 6. 포지셔닝 리포트 생성 테스트
    print("\n" + "=" * 60)
    print("📄 Test 3: generate_positioning_report()")
    print("=" * 60)
    report = analyzer.generate_positioning_report('STORE0001')
    print(report)

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_stp_analyzer()
