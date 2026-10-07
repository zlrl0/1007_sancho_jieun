# Qwen 공식 프롬프트 4B·8B RRF 비교

실행일: 2026-10-07

기존 12편·862개 청크·v2 다중논문 30문항. 한국어/영어 각각 top25 → RRF(60, 동일 가중치) → 최종 25개.

| 조건 (한국어 / 영어) | FullHit@5 | @10 | @20 | @25 | 부분 점수@25 | 논문 근거 |
|---|---:|---:|---:|---:|---:|---:|
| A: 4B / BGE-m3-ko | 10/30 | 15/30 | 22/30 | 23/30 | 89.44% | 72/82 |
| B: 8B / BGE-m3-ko | 8/30 | 15/30 | 22/30 | 22/30 | 87.78% | 71/82 |
| C: 4B / 4B | 12/30 | 17/30 | 22/30 | 22/30 | 86.39% | 70/82 |
| D: 8B / 8B | 13/30 | 15/30 | 21/30 | 23/30 | 88.33% | 71/82 |

## 4B → 8B 문항 변화

- A -> B: -1문항. 새 적중: 없음. 적중 상실: r14.
- C -> D: +1문항. 새 적중: r25. 적중 상실: 없음.

## 설정과 검증

```text
Instruct: Given a web search query, retrieve relevant passages that answer the query
Query:{question}
```

- Qwen/Qwen3-Embedding-4B와 Qwen/Qwen3-Embedding-8B: 질문에만 위 공식 프롬프트. BGE는 dragonkue/BGE-m3-ko, 무프롬프트.
- Qwen 기본 차원 4B=2560, 8B=4096. bfloat16, SDPA, 배치 1, 왼쪽 패딩, 정규화 float32 벡터 및 코사인 검색. 동점은 코퍼스 순서.
- 문서 벡터와 4B/BGE 질문 벡터는 검증 후 재사용. 8B 질문 60개만 새로 임베딩. 유료 API 및 답변 생성 없음.
- 기존 공식 프롬프트 4B 결과의 최종 목록·채점 60개 및 4B/BGE 언어별 top20 120개를 재현. 원본 입력·벡터·결과 해시 불변 확인.
- FullHit는 모든 필수 논문의 허용 근거 청크를 찾은 문항 수. 부분 점수는 문항별 필수 논문 적중 비율의 평균.
- 같은 30문항의 탐색적 비교이며 작은 차이로 통계적 우위를 주장하지 않는다. v2 정답·번역의 사람 검수 대기 상태를 유지하며 생성 답변 정확도를 의미하지 않는다.
- queries.npy와 query_manifest.json은 indexes/q8/, 문항별 순위·채점·변화는 results/, 실행 설정 및 출처는 experiment_plan.json에 저장.

## 문항별 FullHit@25

| 문항 | A | B | C | D |
|---|---:|---:|---:|---:|
| r01 | O | O | O | O |
| r02 | O | O | O | O |
| r03 | O | O | O | O |
| r04 | O | O | O | O |
| r05 | O | O | O | O |
| r06 | O | O | O | O |
| r07 | O | O | O | O |
| r08 | X | X | X | X |
| r09 | O | O | O | O |
| r10 | X | X | X | X |
| r11 | O | O | O | O |
| r12 | O | O | O | O |
| r13 | X | X | X | X |
| r14 | O | X | O | O |
| r15 | O | O | O | O |
| r16 | X | X | X | X |
| r17 | O | O | O | O |
| r18 | O | O | O | O |
| r19 | O | O | O | O |
| r20 | X | X | X | X |
| r21 | O | O | O | O |
| r22 | O | O | O | O |
| r23 | O | O | O | O |
| r24 | O | O | X | X |
| r25 | X | X | X | O |
| r26 | O | O | O | O |
| r27 | O | O | O | O |
| r28 | O | O | O | O |
| r29 | X | X | X | X |
| r30 | O | O | O | O |
