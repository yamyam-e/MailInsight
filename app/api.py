import os, requests
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from gmail_search import gmail_search

app = FastAPI(title="MailInsight", description="Gmail search & auto reply draft", version="1.0")
templates = Jinja2Templates(directory="templates")

# -------------------------------
# 문의 메일 필터링 & 자동 답장 초안
# -------------------------------
def generate_reply_draft(subject: str, snippet: str) -> str:
    prompt = f"""
다음 메일 제목과 요약을 보고, 고객에게 보낼 공손한 답장 초안을 작성해줘.
형식: 인사 → 문의 확인 → 기본 답변 → 추가 문의 안내 → 마무리
메일 제목: {subject}
메일 요약: {snippet}
"""
    # 간단히 Ollama phi4 사용 (openai_compat도 동일 방식으로 추가 가능)
    url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434") + "/api/chat"
    body = {
        "model": os.getenv("LLM_MODEL", "phi4"),
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    resp = requests.post(url, json=body, timeout=60)
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/inquiries", response_class=HTMLResponse)
def inquiries_page(request: Request):
    items = gmail_search("subject:문의 OR 문의", max_results=10)
    return templates.TemplateResponse("inquiries.html", {"request": request, "results": items})

@app.get("/inquiries/reply", response_class=HTMLResponse)
def inquiry_reply_page(request: Request, id: str):
    items = gmail_search(f"id:{id}", max_results=1)
    if not items:
        return templates.TemplateResponse("reply.html", {
            "request": request, "subject": "(메일을 찾을 수 없음)", "snippet": "", "draft": "생성 실패"
        })
    mail = items[0]
    draft = generate_reply_draft(mail["subject"], mail["snippet"])
    return templates.TemplateResponse("reply.html", {
        "request": request, "subject": mail["subject"], "snippet": mail["snippet"], "draft": draft
    })

def classify_with_phi4(subject: str, snippet: str) -> bool:
    prompt = f"""
다음 이메일이 '문의 메일(질문, 요청, 문의사항)'인지 판단해줘.
메일 제목: {subject}
메일 요약: {snippet}
답변은 'YES' 또는 'NO' 만.
"""
    url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434") + "/api/chat"
    body = {
        "model": os.getenv("LLM_MODEL", "phi4"),
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    resp = requests.post(url, json=body, timeout=60)
    resp.raise_for_status()
    answer = resp.json()["message"]["content"].strip().upper()
    return "YES" in answer

@app.get("/inquiries/phi4", response_class=HTMLResponse)
#def inquiries_phi4_page(request: Request, max_results: int = 20):
#    items = gmail_search("", max_results=max_results)
#    inquiries = [m for m in items if classify_with_phi4(m["subject"], m["snippet"])]
#    return templates.TemplateResponse("inquiries_phi4.html", {"request": request, "results": inquiries})
def inquiries_phi4_page(request: Request):
    after, before = _today_range_str()
    # 오늘자 전체 메일
    q = f"after:{after} before:{before}"
    items = gmail_search(q, max_results=200)

    inquiries = []
    for m in items:
        if classify_with_phi4(m["subject"], m["snippet"]):
            draft = generate_reply_draft(m["subject"], m["snippet"])
            inquiries.append({**m, "draft": draft})

    return templates.TemplateResponse(
        "inquiries_phi4.html",
        {"request": request, "results": inquiries, "after": after, "before": before}
    )

# (A) 오늘 날짜 범위 계산 유틸
def _today_range_str():
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST)
    start = datetime(year=now.year, month=now.month, day=now.day, tzinfo=KST)
    end = start + timedelta(days=1)
    after = start.strftime("%Y/%m/%d")
    before = end.strftime("%Y/%m/%d")
    return after, before
