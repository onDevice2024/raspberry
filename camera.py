import time
from picamera2 import Picamera2
import cv2
import zmq
import numpy as np

def capture_and_send_frames(picam2, frame_interval=0.5):
    """
    Capture frames at a specific interval, add a timestamp, and send them as NumPy arrays using ZeroMQ.
    """
    # ZeroMQ 설정
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind("tcp://*:5555")  # ZeroMQ로 데이터를 보낼 주소

    print("Camera started. Sending frames via ZeroMQ...")
    try:
        while True:
            # 프레임 캡처
            image = picam2.capture_array()

            # 타임스탬프 추가
            timestamp = time.strftime("%Y-%m-%d %X")
            origin = (10, 30)  # 텍스트 위치
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = 1
            colour = (255, 255, 255)
            thickness = 2
            cv2.putText(image, timestamp, origin, font, scale, colour, thickness)

            # 프레임과 타임스탬프를 전송
            socket.send_pyobj({"frame": image, "timestamp": timestamp})
            print(f"Frame sent with timestamp: {timestamp}")

            # 지정된 간격만큼 대기
            time.sleep(frame_interval)
    except KeyboardInterrupt:
        print("Camera stream stopped.")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    # Initialize Picamera2
    picam2 = Picamera2()

    # Configure the camera
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)

    # Start the camera
    picam2.start()
    time.sleep(2)  # Let the camera warm up

    # Start capturing and sending frames
    capture_and_send_frames(picam2, frame_interval=0.5)  # 초당 약 2개의 프레임

    # Stop the camera
    picam2.stop()

#pip install pyzmq
