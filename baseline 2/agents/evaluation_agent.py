from langchain_google_genai import ChatGoogleGenerativeAI


def evaluation_agent_node(state: dict) -> dict:
    """전략 카드 평가"""
    
    checks = []
    total_cards = len(state["strategy_cards"])
    passed_cards = 0
    
    for idx, card in enumerate(state["strategy_cards"]):
        check_result = {
            "card_idx": idx,
            "card_title": card.get("title", "제목없음"),
            "constraint_fit": True,
            "evidence_match": True,
            "feasibility": True,
            "issues": []
        }
        
        # 검증 로직
        budget_limit = state["constraints"].get("budget_krw", float('inf'))
        card_budget = card.get("constraints_applied", {}).get("budget_krw", 0)
        
        if card_budget > budget_limit:
            check_result["constraint_fit"] = False
            check_result["issues"].append(f"예산 초과")
        
        if all([check_result["constraint_fit"], 
                check_result["evidence_match"], 
                check_result["feasibility"]]):
            passed_cards += 1
            check_result["status"] = "PASS"
        else:
            check_result["status"] = "FAIL"
        
        checks.append(check_result)
    
    eval_report = {
        "summary": f"{passed_cards}/{total_cards} 카드 적합",
        "pass_rate": passed_cards / total_cards if total_cards > 0 else 0,
        "checks": checks,
        "overall_quality": "우수" if passed_cards == total_cards else "개선 필요",
        "recommendations": []
    }
    
    return {
        "eval_report": eval_report,
        "logs": [f"[evaluation_agent] 평가 완료: {eval_report['summary']}"]
    }