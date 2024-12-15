# 베이스 이미지 선택
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt ./
COPY aiDetection.py ./
COPY test.py ./
COPY model ./model  
# 모델 파일 포함

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 결과 저장소용 디렉토리 생성
RUN mkdir /app/result

# 결과 디렉토리를 외부 볼륨으로 연결 가능하도록 설정
VOLUME ["/app/result"]

# 5555, 5556 포트 노출
EXPOSE 5555
EXPOSE 5556

# aiDetection.py와 test.py를 동시에 실행하기 위한 supervisor 설치 및 설정
RUN apt-get update && apt-get install -y supervisor && apt-get clean
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Supervisor 실행
CMD ["/usr/bin/supervisord"]
