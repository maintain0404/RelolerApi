### 로컬 개발용 서버 켜기
python manage.py runserver --settings RelolerApi.setting.develop_local

### 가상환경 켜기
./RelolerApiEnv\Scripts\activate

## 깃 머지하기
머지 명령을 수행하면 충돌된 부분이 생긴다.
git status로 충돌된 부분을 확인하고
해당 파일을 수정 후 git add로 스테이징한다.
그 후 커밋하면 머지가 완료된다.

## additional commands
curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.python.sh | bash

pwd | cat >> $(which python | xargs dirname | xargs dirname | xargs echo)/lib/python3.7/site-packages/custom_path.pth