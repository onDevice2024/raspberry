import zmq
import numpy as np
import cv2
from ultralytics import YOLO
import os


def detect_kickboards():
    try:
        # ZeroMQ 설정
        context = zmq.Context()

        # REPLY 소켓: 카메라 모듈과 연결
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")

        # PUSH 소켓: 신호를 test.py로 보냄
        push_socket = context.socket(zmq.PUSH)
        push_socket.bind("tcp://*:5556")  # 신호 전송용 포트

        # YOLOv8 모델 로드
        model = YOLO('./model/best_n.pt')

        print("AI Detection Module Started.")

        # 탐지 상태를 저장할 변수
        detection_count = 0  # 연속 탐지 횟수

        while True:
            try:
                # 카메라 모듈에서 데이터 수신
                data = socket.recv_pyobj()
                frame = data["frame"]
                timestamp = data["timestamp"]

                # 프레임이 NumPy 배열인지 확인
                if not isinstance(frame, np.ndarray):
                    raise ValueError("Received frame is not a valid NumPy array")

                # YOLO 모델 추론
                results = model(frame)

                # 감지된 클래스별 객체 수 초기화
                class_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # 클래스 ID: 갯수 매핑

                # 감지된 객체들을 순회하며 카운트
                for box in results[0].boxes:
                    class_id = int(box.cls)
                    class_counts[class_id] += 1

                    # 바운딩 박스와 라벨 추가
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # 바운딩 박스 좌표
                    confidence = box.conf[0]  # 신뢰도
                    label = f"{model.names[class_id]} {confidence:.2f}"

                    # 바운딩 박스와 라벨 그리기
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 초록색 박스
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 조건 충족 확인
                if class_counts[0] >= 1 and class_counts[2] >= 1:  # No_Helmet >= 1, more_than_two >= 1
                    detection_count += 1
                else:
                    detection_count = 0  # 조건이 충족되지 않으면 초기화

                # 조건이 3번 연속 충족되었을 경우 프레임 저장 및 신호 전송
                if detection_count == 3:
                    filename = f"./result/{timestamp.replace(':', '-')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"Frame with annotations saved as {filename}")

                    # test.py에 신호 전송
                    push_socket.send_string(f"Alert at {timestamp}")
                    print(f"Signal sent to test.py: Alert at {timestamp}")

                # 감지 결과와 타임스탬프 출력
                print(f"Detection Results at {timestamp}")

                # 응답 전송
                socket.send_string("Processed")

            except Exception as e:
                # 처리 중 오류 발생 시
                print(f"Error during detection: {e}")
                socket.send_string("Error")

    except Exception as e:
        print(f"Initialization failed: {e}")

if __name__ == "__main__":
    os.makedirs("./result", exist_ok=True)
    detect_kickboards()
