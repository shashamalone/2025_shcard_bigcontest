from langchain.tools import tool
import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "mct_sample.csv")

# 전역에서 CSV 로드
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    df = pd.DataFrame()  # 파일이 없으면 빈 데이터프레임

@tool("search_merchant")
def search_merchant(name: str):
    """
    가맹점명을 받아 로컬 CSV에서 정보를 검색한다.
    반환: 가맹점명, 업종, 상권, 주소, 매출 관련 일부 지표
    """
    if df.empty:
        return {"error": f"데이터 파일을 찾을 수 없음 ({DATA_PATH})"}

    # '가맹점명' 컬럼에서 검색
    result = df[df["가맹점명"].str.contains(name, case=False, na=False)]

    if result.empty:
        return {"error": f"'{name}' 관련 데이터를 찾을 수 없음"}

    # 결과에서 보여줄 주요 컬럼만 추출
    selected = result[
        [
            "가맹점명",
            "가맹점주소",
            "업종",
            "상권",
            "매출금액 구간",
            "매출건수 구간",
            "유니크 고객 수 구간",
            "객단가 구간",
            "취소율 구간",
        ]
    ]

    return selected.to_dict(orient="records")