import torch
import zmq  # ZeroMQ for inter-process communication
import cv2
from ultralytics import YOLO

def detect_kickboards():
    # ZeroMQ 설정
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://localhost:5555")  # 카메라 모듈과 연결

    # YOLOv8 모델 로드
    model = YOLO('best.pt')

    while True:
        # 카메라 모듈에서 데이터 수신
        data = socket.recv_pyobj()
        frame = data["frame"]          # 프레임
        timestamp = data["timestamp"]  # 타임스탬프

        # YOLO 모델 추론
        results = model(frame)

        # 감지된 클래스별 객체 수 초기화
        class_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # 클래스 ID: 갯수 매핑

        # 감지된 객체들을 순회하며 카운트
        for box in results[0].boxes:
            class_id = int(box.cls)
            class_counts[class_id] += 1

        # 조건 충족 시 출력
        if class_counts[0] >= 1 and class_counts[2] >= 1:  # No_Helmet >= 1, more_than_two >= 1
            print("Alert: Dangerous situation detected!")
            print(f"No_Helmet count: {class_counts[0]}")
            print(f"More_than_two count: {class_counts[2]}")

        # 감지 결과와 타임스탬프 출력
        print(f"Detection Results at {timestamp}")

        # 결과 시각화
        annotated_frame = results[0].plot()

        # 시각화된 결과 저장 (선택적으로 실행)
        # cv2.imwrite("output.jpg", annotated_frame)

if __name__ == "__main__":
    detect_kickboards()
