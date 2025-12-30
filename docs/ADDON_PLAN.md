# JPDB 빈도수 Anki 애드온 구현 계획

## 목표 설명
JPDB.io API를 사용하여 Anki 카드의 특정 필드(예: "Expression")에 있는 일본어 단어의 빈도수를 가져와 "Frequency" 필드에 자동으로 채워주는 Anki 애드온을 개발합니다.

## 사용자 검토 필요 사항
> [!IMPORTANT]
> **API 키**: 이 애드온을 사용하려면 사용자의 JPDB API 키가 필요합니다.
> **필드 이름**: 일본어 단어가 있는 소스 필드와 빈도수를 저장할 타겟 필드의 이름을 설정해야 합니다. (기본값 제공)

## 제안된 변경 사항
현재 작업 공간에 `jpdb-frequency-addon` 디렉토리를 생성합니다. 사용자는 추후 이 폴더를 Anki 애드온 폴더에 설치해야 합니다.

### 애드온 구조 (Addon Structure)

#### [NEW] [jpdb-frequency-addon/__init__.py](file:///c:/Users/user/Desktop/Anki-Card-Template/jpdb-frequency-addon/__init__.py)
- 메인 진입점 (Entry point).
- Anki 브라우저 메뉴에 훅(Hook)을 추가합니다.
- "Fill JPDB Frequency" 액션을 등록합니다.

#### [NEW] [jpdb-frequency-addon/manifest.json](file:///c:/Users/user/Desktop/Anki-Card-Template/jpdb-frequency-addon/manifest.json)
- 애드온 메타데이터 (이름, 패키지 정보 등).

#### [NEW] [jpdb-frequency-addon/config.json](file:///c:/Users/user/Desktop/Anki-Card-Template/jpdb-frequency-addon/config.json)
- 설정 관리:
    - `api_key`: 사용자의 JPDB API 토큰.
    - `source_field`: 일본어 텍스트가 있는 필드 (기본값: "Expression").
    - `target_field`: 빈도수를 저장할 필드 (기본값: "Frequency").
    - `overwrite`: 기존 데이터 덮어쓰기 여부 (기본값: false).

#### [NEW] [jpdb-frequency-addon/utils.py](file:///c:/Users/user/Desktop/Anki-Card-Template/jpdb-frequency-addon/utils.py)
- **JPDB 클라이언트**: `https://jpdb.io/api/v1/parse` 엔드포인트와 통신하는 함수.
- **노트 업데이트 로직**: 선택된 노트들을 순회하며 빈도수를 가져오고 필드를 업데이트합니다.
- **진행 상황 표시**: Anki의 진행 상황 관리자(Progress Manager)를 사용하여 작업 진행률을 표시합니다.

### API 로직
- **엔드포인트**: `POST https://jpdb.io/api/v1/parse`
- **요청 데이터**: `{"text": "단어", "token_fields": ["frequency"]}`
- **응답 처리**: 응답에서 빈도수 정보를 추출합니다. 여러 토큰이 반환될 경우(예: 문장), 첫 번째 토큰이나 가장 희귀한 단어를 선택하는 등의 전략이 필요할 수 있습니다. (초기 버전은 1:1 매핑 가정)

## 검증 계획 (Verification Plan)

### 수동 검증
1.  **설치**: `jpdb-frequency-addon` 폴더를 Anki 애드온 디렉토리에 복사합니다.
2.  **설정**: Anki를 실행하고 도구 -> 애드온 -> 설정에서 API 키와 필드 이름을 설정합니다.
3.  **테스트**:
    -   브라우저(탐색기)를 엽니다.
    -   일본어 단어가 포함된 카드를 몇 개 선택합니다.
    -   우클릭 또는 메뉴에서 "Fill JPDB Frequency"를 선택합니다.
    -   진행 표시줄이 나타나는지 확인합니다.
    -   "Frequency" 필드에 숫자가 올바르게 채워지는지 확인합니다.
    -   JPDB 웹사이트와 비교하여 빈도수가 정확한지 확인합니다.
