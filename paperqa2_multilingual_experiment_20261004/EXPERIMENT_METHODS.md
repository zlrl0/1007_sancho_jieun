# PaperQA2 한국어·영어 질문 임베딩 비교 실험

작성일: 2026-10-04  
상태: 검색·답변 생성 48건 완료, 질문·번역 및 답변의 사람 검수 대기

이 문서는 계획만이 아니라 저장된 실행 코드, 고정 프로토콜, 인덱스 메타데이터와 최종 결과를 바탕으로 실제 진행 방법을 정리한 기록이다. 문서를 작성하면서 추가 모델 실행이나 API 호출은 하지 않았다.

## 1. 목적과 실험 범위

같은 다중논문 질문을 한국어와 영어로 각각 검색할 때, 하나의 임베딩 모델을 공통으로 사용하는 것보다 질문 언어에 따라 다른 모델을 사용하는 것이 유리한지 비교했다. 두 언어 질문 모두 최종 답변과 중간 요약은 한국어로 생성하도록 설정했다.

고정된 논문 조각에 대한 **dense 검색 → PaperQA2의 근거 요약·관련도 평가(RCS) → 답변 생성**을 비교했다. 외부 논문 검색, 인용 추적, 에이전트의 반복 탐색, 자동 질문 확장은 사용하지 않았다. 따라서 PaperQA2 논문의 전체 에이전트 시스템을 재현한 실험으로 해석하지 않는다.

## 2. 사용한 논문과 질문

| 항목 | 실제 입력 |
|---|---|
| 논문 조각 | `../chunks/chosen_SEC_none.jsonl`의 862개 조각 |
| 논문 메타데이터 | `../papers.json`의 12편 |
| 원본 다중논문 문항 | `../multi_[12].json`의 6문항 |
| 한국어·영어 질문 쌍 | [questions_ko_en.json](questions_ko_en.json)의 12개 언어 버전 |
| 정답 근거 | evidence 14개, 서로 다른 논문 9편 |
| 나머지 논문 | 정답 근거에 포함되지 않은 3편도 검색 대상에 유지 |

기존에 파싱·청킹된 `text`를 그대로 사용했다. PDF를 다시 파싱하거나 조각을 다시 나누지 않았고, 문서 번역·언어별 필터링·임베딩 입력에 절 제목 추가도 하지 않았다. `chunk_id`, `doc_id`, `section`, `pages` 등은 메타데이터로 보존했다. 참고자료인 `PaperQA2.pdf`는 검색 코퍼스에 추가하지 않았다.

한국어 질문·기준 정답·evidence는 원본에서 그대로 복사하고 영어 질문과 기준 정답 번역을 추가했다. 검색에는 각 언어의 질문을 그대로 사용했으며, 영어 질문을 다시 한국어로 번역해 검색하지 않았다. 기준 정답과 gold evidence 목록은 검색기나 생성 모델에 전달하지 않고 채점에만 사용했다.

`reviewed`와 `translation_reviewed`는 사람 검수가 끝났다는 의미이므로 false 상태를 유지했다. 사용자의 실행 승인은 이와 별도로 기록했다.

## 3. 실행 환경

기존 환경을 변경하지 않고 이 실험 폴더 안에 `.venv`, `model_cache`, `indexes`, `results`, `logs`, `tmp`를 만들었다. 기존 환경의 PyTorch는 CPU 전용이어서 새 환경에 CUDA 지원 PyTorch를 설치했다.

| 항목 | 실행 환경 |
|---|---|
| 운영체제 | Windows 11 Pro |
| CPU / RAM | AMD Ryzen 9 5900X / 약 128 GiB |
| GPU | NVIDIA GeForce RTX 3090 Ti, 24 GB |
| Python | 3.12.10 |
| paper-qa | 2026.8.12 |
| PyTorch | 2.13.0+cu126 |
| sentence-transformers | 6.1.0 |
| transformers | 5.17.0 |
| openai | 2.54.0 |

설치 패키지 기록은 [requirements.lock.txt](requirements.lock.txt), 각 모델의 revision·차원·dtype·프롬프트·길이·GPU 메모리 기록은 `indexes/<모델>/manifest.json`에 있다. Qwen 4B는 GPU에서 정상 실행됐으며, 기록된 최대 할당 GPU 메모리는 약 8.45 GiB였다. 작은 모델로 대체하거나 양자화하지 않았다.

## 4. 비교한 모델과 조합

| 약칭 | 정확한 모델 ID | 벡터 차원 |
|---|---|---:|
| BGE | `dragonkue/BGE-m3-ko` | 1,024 |
| KURE | `nlpai-lab/KURE-v1` | 1,024 |
| OpenAI small | `text-embedding-3-small` | 1,536 |
| Qwen | `Qwen/Qwen3-Embedding-4B` | 2,560 |

| 조건 | 한국어 질문 모델 | 영어 질문 모델 | 구분 |
|---|---|---|---|
| C1 | BGE | BGE | 단일 모델 대조군 |
| C2 | KURE | KURE | 단일 모델 대조군 |
| C3 | BGE | OpenAI small | 언어별 분리 |
| C4 | KURE | OpenAI small | 언어별 분리 |
| C5 | BGE | Qwen | 언어별 분리 |
| C6 | KURE | Qwen | 언어별 분리 |
| C7 | OpenAI small | OpenAI small | 단일 모델 대조군 |
| C8 | Qwen | Qwen | 단일 모델 대조군 |

모델마다 전체 862개 조각을 임베딩한 독립 인덱스를 만들었다. 질문 임베딩과 검색할 문서 인덱스는 반드시 같은 모델을 사용했다. 서로 다른 모델의 벡터나 유사도 점수를 섞지 않았다.

실제 실행 수는 **4모델 × 2언어 × 6문항 = 48건**, 반복 수는 1회다. 이 결과를 8조합의 96개 논리적 평가 칸에 재사용했다. 예를 들어 BGE의 한국어 결과는 C1·C3·C5에서 동일하다. 이를 새로운 실행이나 독립 반복 관측으로 세지 않았다.

## 5. 임베딩과 검색 절차

구현: [src/build_indexes.py](src/build_indexes.py), [src/run_experiment.py](src/run_experiment.py)

1. 각 모델로 문서 862개와 질문 12개를 임베딩했다.
2. BGE·KURE·Qwen은 Sentence Transformers로 GPU에서 BF16, batch size 1, SDPA 설정으로 실행했다. 모델 정의의 pooling을 사용했다.
3. Qwen은 질문에만 모델에 저장된 공식 `query` 프롬프트를 적용했다. 문서에는 적용하지 않았다. BGE·KURE에는 별도 질문 지시문을 추가하지 않았다.
4. OpenAI small은 Embeddings API를 이용했고 기본 1,536차원을 유지했다.
5. 모델별 토큰 길이를 확인하고 입력 상한을 넘으면 중단하도록 했다. 조각을 임의로 자르지 않았다.
6. 벡터를 L2 정규화해 float32로 저장하고 cosine similarity로 검색했다.
7. PaperQA2에 미리 계산한 벡터와 원본 조각을 등록했다. 질문도 저장된 벡터를 사용했다.
8. 최초 검색 상위 20개를 순위·점수·chunk_id와 함께 저장했다. 상위 5·10·20개 적중률을 계산하되, 실제 요약·답변 파이프라인에는 상위 10개를 사용했다.

`texts_index_mmr_lambda=1.0`으로 설정했다. sparse 검색, BM25, hybrid 결합, RRF, 별도 cross-encoder reranker는 사용하지 않았다. PaperQA2의 검색 순서를 저장하고 cosine 점수 경계와 상위 10개 일치 여부를 코드로 검사했다.

## 6. PaperQA2 요약·답변 생성

| 항목 | 실제 고정값 |
|---|---|
| 요약 모델 / 답변 모델 | 모두 `gpt-4.1-mini` |
| temperature | 0 |
| 요약 대상 조각 수 | 10개 |
| 요약 지시 길이 | about 100 words |
| 요약 출력 토큰 상한 | 호출당 1,200 |
| 답변 출력 토큰 상한 | 호출당 1,600 |
| 답변 근거 수 | 최대 5개 |
| 관련도 점수 기준 | 1 이상 |
| 요약·답변 언어 | 한국어 |

각 질문·언어·모델 조합에 새 `PQASession`을 사용했다. `Docs.aget_evidence()`로 조각별 요약과 0~10 관련도 점수를 생성하고, 관련도 내림차순 및 조각 이름 순으로 정렬했다. 상위 5개 중 점수 1 이상인 근거를 답변 입력으로 기록하고 `Docs.aquery()`로 답변을 생성했다.

PaperQA2의 기본 요약·답변 프롬프트에 한국어 출력, 수치·단위·조건 보존, 근거에 없는 값 추측 금지를 추가했다. 실제 프롬프트 전문은 [logs/frozen_protocol.json](logs/frozen_protocol.json)에 저장돼 있다. 근거가 없는 경우의 내부 영어 응답은 원문을 보존하고 표시용 답변만 한국어로 처리하도록 구현했다.

API 전송 부분에는 비용 기록용 `BudgetLLM` 어댑터를 사용했다. 근거 요약 결과 해석, 컨텍스트 구성, 답변 생성 연결은 PaperQA2를 사용했다. API 키 값은 결과에 기록하지 않았다.

## 7. 조각 단위 채점

채점 구현: [src/common.py](src/common.py)의 `hit()`

문항 q의 근거 논문 d마다, 해당 논문의 evidence에 적힌 기본 `chunk_id`와 `alt_chunk_ids`의 합집합을 정답 인정 집합으로 삼았다. 검색하거나 인용한 조각 집합과 이 집합이 하나라도 겹치면 해당 논문을 적중으로 처리했다. 같은 논문의 다른 조각을 찾았다는 이유만으로 적중 처리하지 않았다.

- **완전 적중:** 문항이 요구한 모든 근거 논문이 적중하면 1, 아니면 0.
- **부분 점수:** 적중한 근거 논문 수 / 해당 문항의 전체 근거 논문 수.
- **조합 점수:** 해당 조합의 한국어 6건과 영어 6건을 합산하거나 평균해 계산.

다음 단계를 구분해 저장했다.

| 단계 | 저장 필드 / 의미 |
|---|---|
| 최초 검색 | `retrieved_top20`, `retrieval_metrics`: FullHit@5·10·20 및 부분 점수 |
| RCS 후 | `rcs_contexts`, `stage_metrics.after_rcs` |
| 답변 입력 | `answer_input_contexts`, `stage_metrics.answer_input` |
| 실제 인용 | `cited_chunk_ids`, `stage_metrics.cited` |

실제 인용은 답변의 `pqac-...` 인용 키를 답변 입력 근거의 원본 chunk_id로 연결해 판정했다. **조각 적중률은 답변 정답률이 아니다.** 답변의 수치·조건·논문 간 대응과 인용의 적절성은 사람이 별도로 검수해야 한다.

## 8. 완료 결과

아래 값은 [results/summary_report.json](results/summary_report.json)의 완료 결과다.

| 조건 | 한국어 / 영어 모델 | 검색 완전 적중@10 | 논문별 부분 점수 평균@10 | 답변 입력 완전 적중 | 실제 인용 완전 적중 |
|---|---|---:|---:|---:|---:|
| C1 | BGE / BGE | 3/12 | 56.94% | 3/12 | 3/12 |
| C2 | KURE / KURE | 3/12 | 56.94% | 3/12 | 2/12 |
| C3 | BGE / OpenAI small | 2/12 | 45.83% | 2/12 | 2/12 |
| C4 | KURE / OpenAI small | 2/12 | 48.61% | 2/12 | 2/12 |
| C5 | BGE / Qwen | 3/12 | 59.72% | 3/12 | 2/12 |
| C6 | KURE / Qwen | 3/12 | 62.50% | 3/12 | 2/12 |
| C7 | OpenAI small / OpenAI small | 0/12 | 29.17% | 0/12 | 0/12 |
| C8 | Qwen / Qwen | 4/12 | 66.67% | 3/12 | 2/12 |

| 임베딩 모델 | 한국어 검색 완전 적중@10 | 영어 검색 완전 적중@10 |
|---|---:|---:|
| BGE | 2/6 | 1/6 |
| KURE | 2/6 | 1/6 |
| OpenAI small | 0/6 | 0/6 |
| Qwen | 3/6 | 1/6 |

이번 결과에서는 Qwen을 두 언어에 공통으로 사용한 C8이 검색 완전 적중과 부분 점수에서 가장 높았다. BGE·KURE의 영어 모델을 Qwen으로 교체하면 부분 점수는 증가했지만 완전 적중 수는 같았고, OpenAI small로 교체하면 완전 적중 수가 감소했다. 언어별 분리 조합이 가장 좋은 단일 모델 대조군을 넘어서는 결과는 관찰되지 않았다.

그러나 최종 인용까지 모든 근거가 남은 문항 수는 C1이 가장 많았다. C8의 검색 완전 적중 4건은 답변 입력에서 3건, 실제 인용에서 2건으로 줄었다. 따라서 Qwen의 검색 결과만으로 최종 답변 품질까지 가장 좋다고 결론 내릴 수 없다.

## 9. 비용과 검증

총 API 비용은 캐시 할인을 적용하지 않은 사용량 기반 계산으로 **$0.34927332**다. 승인된 상한 $3 이내이며, 미확정 예약 금액은 0이다. 이 금액은 로컬 GPU의 전기료·장비 비용을 포함하지 않으며 실제 청구서 금액과는 구분한다.

호출은 총 556건으로, 요약·답변 호출 528건과 임베딩 호출 28건이다. 실행 코드가 사용한 계산 단가는 임베딩 100만 토큰당 $0.02, 생성 모델 입력 $0.40·출력 $1.60이다. 이는 이번 실행의 비용 산식이며 향후 실행 시점의 요금 안내가 아니다. 각 호출 전 상한 비용을 예약하고 완료 후 실제 사용량으로 정산했으며, SDK 자동 재시도는 껐다.

[logs/final_validation.json](logs/final_validation.json)에 다음 검증 결과를 기록했다.

- 48개 실행 결과가 모두 존재하고 모델·질문이 일치한다.
- evidence 14개의 chunk_id가 실제 존재하고 doc_id·section·pages가 일치한다.
- answer_span이 원문에 그대로 존재하며, benchmark README의 `norm()` 적용 후에도 포함된다.
- 문항마다 서로 다른 근거 doc_id가 2개 이상이다.
- 저장된 검색·단계별 적중 지표를 다시 계산해 일치함을 확인했다.
- 보호 대상으로 기록한 기존 입력·코드 파일의 해시가 유지됐다.
- 48개 답변에서 한국어 문자가 확인됐다. 이 검사는 언어 존재 확인이며 답변 품질 검수는 아니다.
- 알 수 없는 인용 키가 없고, 요약·답변 API 응답 528건의 종료 사유는 모두 `stop`이다.

초기 검증은 [src/preflight.py](src/preflight.py), 완료 검증은 [src/final_validate.py](src/final_validate.py)로 구현했다. 실행 중에도 입력 해시와 고정 프로토콜이 바뀌지 않았는지 확인했다.

## 10. 결과 해석의 한계와 남은 검수

의미상 독립 질문은 6개뿐이다. 영어 번역본과 조합 간 재사용 결과를 별도의 독립 표본으로 볼 수 없다. 실행도 1회이므로 반복 변동을 측정하지 않았다. 이 결과는 해당 질문·코퍼스·설정에 대한 탐색적 비교이며 일반적인 모델 순위를 확정하지 않는다.

질문은 여러 논문의 실험 방법을 모아 비교하는 데 집중돼 있다. 질문·번역·gold의 사람 검수와 생성 답변의 정답/부분/오답 판정은 아직 남아 있다. 동일한 내용을 담은 다른 조각이라도 gold의 기본 ID나 대체 ID로 등록되지 않았다면 현재 지표에서 적중하지 않는다. 결과를 본 뒤 정답 인정 조각을 바꾸려면 별도 버전과 재채점 기록이 필요하다.

사람 검수용 파일은 [results/answer_review.json](results/answer_review.json)이다. `label`, `reviewed`, `notes`에 검수 내용을 남길 수 있다. 현재 보고서는 이 파일의 답변 정확도를 자동 집계하지 않는다. 검수 후 답변 품질 비교는 별도로 작성해야 한다.

## 11. 파일 안내

| 파일 / 폴더 | 내용 |
|---|---|
| [experiment_plan.json](experiment_plan.json) | 초기 계획, 승인 기록, 완료 상태. 일부 필드에는 실행 전 제안 문구가 남아 있음 |
| [logs/frozen_protocol.json](logs/frozen_protocol.json) | 실제 고정한 프롬프트·생성 설정·입력 해시 |
| [questions_ko_en.json](questions_ko_en.json) | 한국어·영어 질문, 기준 정답, 근거 |
| `indexes/{bge,kure,openai,qwen}/` | `documents.npy`, `queries.npy`, `manifest.json` |
| `results/<모델>_<문항>_<언어>.retrieval.json` | 검색 상위 20개와 최초 검색 지표 |
| `results/<모델>_<문항>_<언어>.json` | 요약, 답변 입력 근거, 한국어 답변, 실제 인용, 단계별 점수 |
| [results/report.html](results/report.html) | 사람이 열어 볼 수 있는 전체 결과와 문항별 답변 |
| [results/summary_report.json](results/summary_report.json) | 모델·언어 및 8개 조합의 집계 |
| [results/answer_review.json](results/answer_review.json) | 사람 검수용 답변 목록 |
| `logs/call_*.json` | 요약·답변 요청, 응답, 토큰 사용량, 비용 기록 |
| `logs/budget.sqlite3` | API 호출별 비용 예약·정산 |
| [logs/final_validation.json](logs/final_validation.json) | 완료 후 검증 결과 |

## 12. 저장된 결과 확인 및 재실행 방법

아래 명령은 PowerShell에서 **이 실험 폴더를 작업 디렉터리로** 사용한다.

```powershell
Set-Location 'C:\Users\je\cislab\benchmark\paperqa2_multilingual_experiment_20261004'
```

### 결과 재집계와 완료 검증 — API 호출 없음

```powershell
.venv/Scripts/python.exe src/final_validate.py
.venv/Scripts/python.exe src/report.py
```

완료 검증은 `logs/final_validation.json`과 계획의 완료 상태를 갱신한다. 보고서 명령은 집계 JSON·HTML·검수 목록을 갱신하며 기존 검수 항목을 보존한다.

### 인덱스 생성·실험 재개 명령

다음은 실제 실행에 사용한 명령 형식이다. **미완료 항목이 있으면 다운로드 또는 유료 API 호출이 발생할 수 있다.** API 키는 실험 폴더의 `.env`, 또는 상위 benchmark 폴더의 `.env`에서 읽는다. 키 값은 문서에 적지 않는다.

```powershell
.venv/Scripts/python.exe src/build_indexes.py bge
.venv/Scripts/python.exe src/build_indexes.py kure
.venv/Scripts/python.exe src/build_indexes.py openai
.venv/Scripts/python.exe src/build_indexes.py qwen

.venv/Scripts/python.exe src/run_experiment.py bge
.venv/Scripts/python.exe src/run_experiment.py kure
.venv/Scripts/python.exe src/run_experiment.py openai
.venv/Scripts/python.exe src/run_experiment.py qwen
```

완성된 인덱스와 실행 결과는 건너뛰므로, 현재 폴더에서 이 명령을 다시 실행하는 것은 독립 반복 실험이 아니다. 중단 후 재개할 때는 저장된 API 응답도 재사용한다. 별도 반복이나 설정 변경 실험은 새 실험 폴더에 입력 경로·프로토콜·비용 기록을 분리해 구성해야 한다. 기존 결과나 캐시를 삭제해 덮어쓰지 않는다.

환경 재구성 시 [requirements.txt](requirements.txt)와 [requirements.lock.txt](requirements.lock.txt)를 참고하되, 이번 환경은 CUDA용 PyTorch 배포본을 설치했다는 점을 함께 반영해야 한다. 모델 revision과 실제 실행 설정은 각 인덱스의 `manifest.json`을 기준으로 확인한다.
