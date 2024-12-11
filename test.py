import zmq

def listen_for_alerts():
    # ZeroMQ 설정
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect("tcp://localhost:5556")  # aiDetection.py에서 PUSH로 보낸 신호 수신

    print("Listening for alerts from aiDetection.py...")
    while True:
        # 신호 수신
        message = socket.recv_string()
        print(f"Received alert: {message}")

if __name__ == "__main__":
    listen_for_alerts()
