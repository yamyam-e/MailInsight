# 📧 MailInsight

문의 메일 자동 분류 및 답변 초안 생성 시스템

---

## 📘 프로젝트 개요
- Gmail API로 수신 메일을 가져와 `phi-4` 모델을 통해 '문의' 여부를 분류합니다.
- 문의 메일에 대해서는 자동으로 정중한 답변 초안을 생성합니다.
- FastAPI + Jinja2 기반 웹 UI를 제공합니다.

---

## 🛠️ 환경
- Python 3.11
- FastAPI
- Jinja2
- Gmail API
- Ollama (phi-4 모델)
- Docker, Docker Compose

---

## 🚀 실행 방법

### 1. Gmail API 준비
- Google Cloud Console → Gmail API 활성화
- OAuth2 Client ID 발급 후 `credentials.json` 다운로드
- 실행 전에 `/secrets/credentials.json` 위치에 배치

### 2. Docker 실행
```bash
docker compose up --build -d
