# 프로젝트 다봄 ( 다이어트 하는거 다 지켜봄 )

[나경원 (PM, DevOps, BackEnd, FrontEnd)](https://github.com/chickiyeah)

[연수아 (FrontEnd, Designer, Publisher)](https://github.com/yppeu)

[오유림 (Designer, Publisher)](https://github.com/yurim)

## Backend
<div>
  <img src="https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=white">
  <img src="https://img.shields.io/badge/python-3776ab?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/mysql-4479a1?style=for-the-badge&logo=mysql&logoColor=white">
  <img src="https://img.shields.io/badge/oralce-f80000?style=for-the-badge&logo=oracle&logoColor=white">
</div>

## Frontend
<div>
  <img src="https://img.shields.io/badge/html5-e34f26?style=for-the-badge&logo=html5&logoColor=white">
  <img src="https://img.shields.io/badge/javascript-f7df1e?style=for-the-badge&logo=javascript&logoColor=white">
  <img src="https://img.shields.io/badge/css3-1572b6?style=for-the-badge&logo=css3&logoColor=white">
</div>

---

## 개요
다봄(DABOM, "다이어트 하는 거 다 지켜봄") — 식단·음식·영양을 기록하고 친구·그룹과 함께 관리하는 다이어트 기록 소셜 앱. FastAPI 백엔드 + 정적 프론트(FrontSide).

## 주요 기능
- **다이어리 기록** (diary)
- **음식 / 영양 정보** (food, nutrient)
- **친구** (friends)
- **그룹** (group)
- **실시간 소통·알림** (websocket, alert)
- **회원** (userapi)

## 기술 스택
- **백엔드**: FastAPI + Uvicorn (Starlette)
- **DB**: MySQL (PyMySQL), Redis
- **인증**: JWT (PyJWT)
- **프론트**: `FrontSide/` (JS/HTML/CSS), StaticFiles로 서빙
- **기타**: CORS, WebSocket

## 실행
```
pip install -r requirements.txt
python mysql_setup.py   # DB 초기화
uvicorn main:app --reload
```

## 디렉터리
- `main.py` — FastAPI 엔트리 (라우터 9개 등록 + 정적 마운트)
- `controller/` — 라우터·로직 (userapi, diary, food, nutrient, friends, group, websocket, alert, Screen, database, onemsgdb)
- `FrontSide/` — 프론트엔드 (JS/HTML/CSS)
- `mysql_setup.py` — DB 셋업
