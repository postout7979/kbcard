# web/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# 가상 환경 생성 (Docker 컨테이너 내부)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Flask 및 requests 라이브러리 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# WEB 서버 코드 복사
COPY web_server.py .

# Flask 앱이 5000번 포트를 사용하도록 노출
EXPOSE 5000

# WEB 서버 실행
CMD ["python", "web_server.py"]
