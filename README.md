# GEYK 홈페이지 검토용 사이트
GitHub Pages 배포 대상: https://goblinok.github.io/geyk/
운영 geyk.org 및 DNS는 변경하지 않습니다. AntTrail 2~4주차는 검토용 초안입니다.

## 기사 시트 반영
사이트는 빌드할 때 Google에 게시된 CSV를 실제로 다운로드합니다. date/title/media/url과 선택 image_url을 유지합니다. Python 서버는 방문자에게 필요하지 않습니다.
GitHub Pages는 정적 호스팅이므로 시트 변경만으로 즉시 갱신되지는 않습니다. 시트 편집 후 이 저장소의 Actions → Deploy GEYK Pages → Run workflow를 실행하세요. 홈페이지의 '목록 새로고침'은 마지막 배포본을 다시 읽습니다. 자동 주기 실행은 설정하지 않았습니다.

## 본문 수정 및 배포
index.html을 수정해 main에 push하면 검증 후 배포합니다. 배포 산출물은 index.html, data/press.csv, data/sync.json, .nojekyll만 포함합니다. 로컬 캐시·브라우저 프로필·키·연구 자료를 배포하지 않습니다.

## 로컬 빌드 확인
python3 scripts/build_pages.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8788 --directory _site

AntTrail 의견은 기존 Apps Script와 주차별로 연결됩니다. 기사 이미지 주소가 없거나 열리지 않으면 GEYK 공통 사진으로 대체합니다. 기사/이미지 사용 권한은 별도로 확인해야 합니다.
