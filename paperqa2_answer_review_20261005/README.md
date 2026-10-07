# Qwen / BGE-m3-ko 한국어 답변 생성·검수 실험

2026-10-05에 답변 생성·검수 결과를 별도 폴더로 이동했습니다. 새로운 모델 실행이나 API 호출은 하지 않았습니다.

- [질문별 답변 검수 HTML](review_20261005/답변검수.html): 30개 질문의 생성 답변·정답·검수 의견·근거 조각을 확인합니다.
- [생성 답변 원문](ANSWERS_KO.md)
- [전체 AI 검수 보고서](review_20261005/검수보고서.md)
- [초기 검증 기록](CHECKS.md): 전체 검수 이전의 기록입니다. 최신 검수는 위 보고서를 보세요.
- `results/`: 30문항 생성 답변과 RCS·인용 정보.
- `logs/`: 요청·응답 기록과 비용 원장. API 키는 포함하지 않습니다.
- `summary.json`: 생성 실행 집계. 답변 내용 검수는 `review_20261005/review.json`을 보세요.

## 조건

한국어 Qwen/Qwen3-Embedding-4B + 영어 dragonkue/BGE-m3-ko → RRF 최종 고유 조각 20개 → PaperQA2 RCS → 상위 최대 5개로 gpt-4.1-mini 한국어 답변 생성.

기존 12편·862개 조각과 v2 30문항을 사용했습니다. 정답은 생성 모델에 제공하지 않았습니다. 검수는 AI 대조 검수이며 사람 검수는 아닙니다. 원래 gold의 reviewed 값은 변경하지 않았습니다.

## 참조하는 기존 파일

- 검색 입력: `../paperqa2_bilingual_fusion_20261004/results/c08.json`
- 질문·정답: `../paperqa2_retrieval_expanded_20261004/v2/questions_ko_en.json`
- 조각: `../chunks/chosen_SEC_none.jsonl`
- 실행 환경·공통 코드: `../paperqa2_multilingual_experiment_20261004/`

HTML은 데이터가 내장된 단일 파일이므로 별도 서버 없이 열 수 있습니다. HTML의 브라우저 자동 화면 검증은 로컬 파일 접근 정책으로 차단됐고, 데이터 무결성과 JavaScript 문법만 검사했습니다.

## 이동 기록

이전 위치: `../paperqa2_bilingual_fusion_20261004/answers_qwen_bge_ko/`

이동 전후 모든 파일의 SHA-256 일치를 확인했습니다(`relocation_files.json`). 실행 코드의 경로만 새 위치에 맞춰 바꿨고, 원래 실행 코드·프로토콜은 `*.before_relocation.*`에 보존했습니다. 생성 답변·로그·HTML·검수 결과는 그대로 유지했습니다. 기존 검색 실험 폴더는 변경하지 않았습니다.
