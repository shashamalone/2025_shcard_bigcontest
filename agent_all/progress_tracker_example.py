"""
진행 상황 표시 기능 예제 - Streamlit UI에 실시간 진행 상황 표시
"""
import streamlit as st
import io
from contextlib import redirect_stdout
import threading
import time

def test_long_running_task():
    """테스트용 긴 작업"""
    print("[Supervisor] 작업 시작")
    time.sleep(1)
    print("[Market Team] STP 분석 중...")
    time.sleep(2)
    print("[4P Strategy] 전략 카드 생성 완료")
    return {"status": "완료"}

st.title("진행 상황 표시 예제")

if st.button("작업 시작"):
    progress_container = st.empty()
    status_messages = []

    def update_progress(message):
        status_messages.append(message)
        recent = status_messages[-5:]
        text = "\n".join([f"• {m}" for m in recent])
        progress_container.markdown(f"""
<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px;">
<h4>🔄 진행 중...</h4>
<pre>{text}</pre>
</div>
        """, unsafe_allow_html=True)

    output_buffer = io.StringIO()

    def monitor_output():
        last_pos = 0
        while threading.current_thread().is_alive():
            output_buffer.seek(last_pos)
            new = output_buffer.read()
            if new:
                for line in new.strip().split('\n'):
                    if line and ('[' in line or '완료' in line):
                        update_progress(line.strip())
                last_pos = output_buffer.tell()
            time.sleep(0.3)

    thread = threading.Thread(target=monitor_output, daemon=True)
    thread.start()

    with redirect_stdout(output_buffer):
        result = test_long_running_task()

    time.sleep(0.5)
    progress_container.empty()
    st.success("✅ 완료!")
