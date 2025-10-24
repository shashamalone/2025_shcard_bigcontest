#!/usr/bin/env python
"""
가맹점 ID 확인 스크립트
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def check_store_ids():
    """가맹점 ID 확인"""
    print("=" * 80)
    print("📊 가맹점 데이터 확인")
    print("=" * 80)

    # 데이터 로드
    df = pd.read_csv(
        DATA_DIR / "store_segmentation_final_re.csv",
        encoding='utf-8-sig'
    )

    print(f"\n✅ 총 가맹점 수: {len(df)}")

    # 업종별 분포
    print("\n📈 업종별 가맹점 수:")
    industry_counts = df['업종'].value_counts()
    for industry, count in industry_counts.items():
        print(f"   {industry}: {count}개")

    # 첫 10개 가맹점 출력
    print("\n🏪 첫 10개 가맹점:")
    display_cols = ['가맹점구분번호', '가맹점명', '업종', '상권', 'cluster_id']
    print(df[display_cols].head(10).to_string(index=False))

    # 샘플 가맹점 ID 추천
    print("\n💡 Streamlit에서 사용할 수 있는 샘플 가맹점 ID:")
    for i in range(min(5, len(df))):
        row = df.iloc[i]
        print(f"   {i+1}. {row['가맹점구분번호']} - {row['가맹점명']} ({row['업종']}, {row['상권']})")

    # 특정 업종별 샘플
    print("\n🎯 업종별 샘플 가맹점:")
    for industry in industry_counts.head(5).index:
        sample = df[df['업종'] == industry].iloc[0]
        print(f"   {industry}: {sample['가맹점구분번호']} - {sample['가맹점명']}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_store_ids()
