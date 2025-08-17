import cv2
import imagezmq

image_hub = imagezmq.ImageHub(open_port='tcp://127.0.0.1:5551', REQ_REP = False)

while True:
    _, image = image_hub.recv_image()
    cv2.imshow("zmq_view", image)
    cv2.waitKey(1)
