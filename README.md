[Agent 추가, test 방법]
- 구현 : Agent 함수 작성 (dict 반환!)
- 테스트 : Jupyter에서 단위 테스트- test_agents
- 통합 : graph.py에 노드 등록

[graph.py에 노드 등록 시 주의]
- (agent) agents/__init__.py에 신규 agent 추가 필수
- (agent) agents/graph.py에서 import 필수
- (스키마) contracts에 필요한 스키마 정의
- 에서 최종 인식 확인 (app.py에서 돌아가려면 테스트 필요)
