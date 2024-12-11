import time
from picamera2 import Picamera2
import cv2
import zmq

def capture_and_send_frames(picam2):
    """
    Capture a frame, add a timestamp, and send it to the AI module. 
    Wait for a response before capturing the next frame.
    """
    # ZeroMQ 설정
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")  # AI 모듈로 데이터를 보낼 주소

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

            # AI 모듈의 응답 대기
            response = socket.recv_string()
            # print(f"AI Module Response: {response}")

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
    capture_and_send_frames(picam2)

    # Stop the camera
    picam2.stop()


#pip install pyzmq
