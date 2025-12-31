# 네이버 일본어 사전 스크래핑 가이드

일본어 단어의 한국어 뜻을 네이버 일본어 사전에서 자동으로 가져오는 스크립트 사용 가이드입니다.

---

## 📋 개요

### 처리 대상
- **noun.csv**: 17,543개 단어
- **verb.csv**: 4,245개 단어
- **adjective.csv**: 1,424개 단어
- **adverb.csv**: 1,428개 단어

**총 24,640개 단어**

### 예상 시간
- **약 10-11시간** (단어당 1.5초 대기)

### 뜻 형식
최대 3개 뜻을 숫자와 함께 가져옵니다:
```
1. 생각하다. 2. 헤아려 판단하다. 3. 예상하다, 헤아리다, 상상하다.
```

---

## 🚀 실행 방법

### 1. 터미널 열기
프로젝트 디렉토리에서 터미널을 엽니다:
```bash
cd C:\dev\Japanese-Anki-Card-Template
```

### 2. 스크립트 실행
```bash
python scrape_meanings.py
```

### 3. 실행 확인
다음과 같은 출력이 나오면 정상 실행된 것입니다:
```
============================================================
Naver Dictionary Scraper - Full Run
============================================================

Processing 4 CSV files:
  - noun.csv: 17,543 entries
  - verb.csv: 4,245 entries
  - adjective.csv: 1,424 entries
  - adverb.csv: 1,428 entries

Total entries to process: 24,640
Estimated time: 10.3 hours

Initializing Chrome WebDriver...
[OK] WebDriver initialized

============================================================
Processing: noun.csv
============================================================
Total entries: 17543
Starting from: 1
  [1/17543] こと... [OK]
  [2/17543] もの... [OK]
  [3/17543] 人... [OK]
  ...
```

---

## 📊 진행 상황 확인

### 방법 1: 터미널 직접 확인
스크립트가 실행 중인 터미널에서 실시간으로 진행 상황을 확인할 수 있습니다.

### 방법 2: 진행 상태 파일 확인
```bash
cat scraping_progress.json
```

출력 예시:
```json
{
  "noun.csv": 523,
  "verb.csv": 0
}
```
→ noun.csv의 523번째 단어까지 완료

### 방법 3: CSV 파일 직접 확인
```bash
head -n 5 resources/pos/noun.csv
```

Meaning 컬럼이 채워지고 있는지 확인할 수 있습니다.

---

## ⏸️ 중단 및 재개

### 중단 방법
터미널에서 `Ctrl + C` 를 누릅니다.

```
^C
[WARNING] Interrupted by user
[INFO] Progress has been saved. Run again to continue.
[INFO] WebDriver closed
```

### 재개 방법
**동일한 명령어로 다시 실행**하면 자동으로 이어서 진행됩니다:
```bash
python scrape_meanings.py
```

출력 예시:
```
Processing: noun.csv
Total entries: 17543
Starting from: 524    ← 중단된 지점부터 시작
```

### 진행 상태 초기화 (처음부터 다시 시작)
```bash
del scraping_progress.json    # Windows
# rm scraping_progress.json   # Mac/Linux
python scrape_meanings.py
```

---

## ✅ 완료 후 확인

### 1. 완료 메시지 확인
```
============================================================
All files completed!
============================================================
[OK] Progress file removed
[INFO] WebDriver closed
```

### 2. 결과 파일 확인
```bash
# 각 파일의 첫 몇 줄 확인
head -n 5 resources/pos/noun.csv
head -n 5 resources/pos/verb.csv
head -n 5 resources/pos/adjective.csv
head -n 5 resources/pos/adverb.csv
```

Meaning 컬럼에 다음과 같이 채워져 있어야 합니다:
```
Frequency,Expression,Reading,Meaning,...
3,こと,,1. 일, 것 2. 사항, 사실, 사정, 사건. 3. 특히 중요한 일,...
23,もの,,1. 것, 물건. 2. 사람. 3. 성질, 성격,...
```

### 3. 통계 확인
완료된 단어 수 확인:
```bash
# Windows PowerShell
(Get-Content resources/pos/noun.csv | Select-String -Pattern "^[0-9]" | Measure-Object).Count

# Git Bash / Linux
grep -c "^[0-9]" resources/pos/noun.csv
```

---

## 🔧 설정 변경

### 처리할 파일 변경
`scrape_meanings.py` 파일의 28번째 줄:
```python
TARGET_FILES = ['noun.csv', 'verb.csv', 'adjective.csv', 'adverb.csv']
```

예: 동사만 처리하려면
```python
TARGET_FILES = ['verb.csv']
```

### 요청 간격 변경
`scrape_meanings.py` 파일의 24번째 줄:
```python
DELAY_BETWEEN_REQUESTS = 1.5  # seconds
```

- **더 빠르게**: `1.0` (네이버 서버에 부담 증가)
- **더 안전하게**: `2.0` (시간은 더 걸림)

---

## ❗ 문제 해결

### 문제 1: "ModuleNotFoundError: No module named 'selenium'"
**해결 방법:**
```bash
python -m pip install selenium webdriver-manager
```

### 문제 2: "WebDriver 초기화 실패"
**해결 방법:**
```bash
# Chrome 브라우저 설치 확인
# Chrome 버전과 ChromeDriver 버전 호환성 확인
python -m pip install --upgrade webdriver-manager
```

### 문제 3: 특정 단어에서 계속 실패
**원인:**
- 네트워크 연결 문제
- 네이버 사전에 해당 단어가 없음

**해결 방법:**
- 스크립트는 3번 재시도 후 실패하면 다음 단어로 넘어갑니다
- 실패한 단어는 Meaning이 빈 문자열("")로 저장됩니다
- 완료 후 수동으로 채울 수 있습니다

### 문제 4: "UnicodeEncodeError"
**원인:**
Windows 콘솔의 인코딩 문제

**해결 방법:**
이 에러는 무시해도 됩니다. 스크립트는 정상 작동하며, 결과 파일은 UTF-8로 올바르게 저장됩니다.

### 문제 5: 중간에 컴퓨터가 꺼졌어요
**해결 방법:**
1. 컴퓨터를 다시 켭니다
2. 프로젝트 디렉토리로 이동
3. 동일한 명령어 실행: `python scrape_meanings.py`
4. 자동으로 마지막 저장 지점부터 이어서 실행됩니다

---

## 📁 생성되는 파일

### 작업 중
- `scraping_progress.json`: 진행 상태 저장 (10개 단어마다 자동 저장)

### 완료 후
- `resources/pos/noun.csv`: 업데이트된 명사 파일
- `resources/pos/verb.csv`: 업데이트된 동사 파일
- `resources/pos/adjective.csv`: 업데이트된 형용사 파일
- `resources/pos/adverb.csv`: 업데이트된 부사 파일

**원본 파일은 덮어쓰여집니다!** 백업이 필요하면 미리 복사해두세요.

---

## 💡 팁

### 1. 백업 먼저 하기
```bash
# 백업 폴더 생성
mkdir resources/pos_backup

# 파일 복사
cp resources/pos/noun.csv resources/pos_backup/
cp resources/pos/verb.csv resources/pos_backup/
cp resources/pos/adjective.csv resources/pos_backup/
cp resources/pos/adverb.csv resources/pos_backup/
```

### 2. 밤새 실행하기
- 노트북을 사용 중이라면 **전원 연결** 필수
- Windows 설정에서 **절전 모드 해제**:
  - 설정 → 시스템 → 전원 및 절전 → 화면 및 절전 모드
  - "연결된 경우 PC를 절전 모드로 전환": **안 함**

### 3. 진행 상황 주기적 확인
아침에 일어나서:
```bash
# 마지막 진행 상황 확인
cat scraping_progress.json

# 또는 실시간 로그 확인 (실행 중인 경우)
# 터미널에서 직접 확인
```

### 4. 특정 품사부터 시작하기
진행 상태 파일을 직접 수정할 수 있습니다:

`scraping_progress.json`:
```json
{
  "noun.csv": 17543,
  "verb.csv": 0
}
```
→ noun.csv를 건너뛰고 verb.csv부터 시작

---

## 📞 추가 도움말

문제가 발생하거나 질문이 있으면:
1. `scraping_progress.json` 파일 내용 확인
2. 터미널 출력 메시지 확인
3. CSV 파일에서 Meaning 컬럼이 어디까지 채워졌는지 확인

행운을 빕니다! 🌙✨
