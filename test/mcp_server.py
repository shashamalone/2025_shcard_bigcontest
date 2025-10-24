# mcp_server.py
import pandas as pd
from mcp.server.fastmcp import FastMCP
from typing import Optional

# FastMCP 서버 초기화
mcp = FastMCP("merchant_data_server")

# 데이터 경로
DATA_PATH = "/mnt/c/Users/rladl/Desktop/bigcontest_2025/2025_shcard_bigcontest/data/df_final.csv"
_df_cache = None

def load_data() -> pd.DataFrame:
    """CSV 데이터 로드"""
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(DATA_PATH,encoding='cp949')
    return _df_cache

@mcp.tool()
def search_merchant(merchant_id: str = "", merchant_name: str = "") -> str:
    """
    가맹점 검색
    
    Args:
        merchant_id: 가맹점 구분번호
        merchant_name: 가맹점명
    """
    df = load_data()
    
    if not merchant_id and not merchant_name:
        return "가맹점 구분번호 또는 가맹점명을 입력해주세요."
    
    if merchant_id:
        results = df[df['ENCODED_MCT'] == merchant_id]
    else:
        results = df[df['MCT_NM'].str.contains(merchant_name, case=False, na=False)]
    
    if len(results) == 0:
        return "검색 결과가 없습니다."
    elif len(results) == 1:
        data = results.iloc[0]
        return f"가맹점 찾음: {data['MCT_NM']} (구분번호: {data['ENCODED_MCT']})"
    else:
        duplicates = "\n".join([
            f"{i+1}. {row['MCT_NM']} - {row['HPSN_MCT_ZCD_NM']} - 구분번호: {row['ENCODED_MCT']}"
            for i, (_, row) in enumerate(results.iterrows())
        ])
        return f"{len(results)}개의 가맹점이 검색되었습니다:\n{duplicates}\n\n가맹점 구분번호를 입력해주세요."

@mcp.tool()
def get_merchant_data(merchant_id: str) -> str:
    """
    가맹점 구분번호로 상세 데이터 조회
    
    Args:
        merchant_id: 가맹점 구분번호
    """
    df = load_data()
    result = df[df['ENCODED_MCT'] == merchant_id]
    
    if len(result) == 0:
        return f"가맹점 구분번호 '{merchant_id}'를 찾을 수 없습니다."
    
    data = result.iloc[0]
    
    output = f"""
가맹점 정보:
- 가맹점명: {data['가맹점명']}
- 가맹점주소 : {data['가맹점주소']}
- 상권: {data['상권']}
- 업종: {data['업종']}
- 개설일: {data['개설일']}
- 폐업일: {data['폐업일'] if pd.notna(data['폐업일']) else '운영 중'}
 

주요 지표:
- 경쟁강도: {data['comp_intensity']:.2f}
- 상권이탈률(4주): {data['market_churn_rate_4w']:.2f}%
- 동일업종매출비중: {data['customer_fit_score']:.2f}
- 고객적합도점수: {data['avg_survival_months']:.2f}
- 평균생존개월수: {data['avg_survival_months']:.0f}개월
- 매출증감률(4주): {data['Δsales_4w']:.2f}%
- 매출변동성(4주): {data['sales_volatility_4w']:.4f}
- 리스크점수: {data['risk_score']:.4f}
"""
    return output.strip()

if __name__ == "__main__":
    mcp.run()