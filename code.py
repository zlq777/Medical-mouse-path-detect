import cv2
import os
import math


def test():
    os.chdir(os.path.join(os.path.dirname(__file__), "./"))
    print(os.getcwd())


def preprocess(src):
    # binary
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    # cv2.imshow('binary', binary)

    # open and close
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # find contours
    res = []
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 0), 2)
        res.append((x, y, w, h))

    # cv2.imshow('src', src)
    res.sort(key=lambda x: x[3] * x[2], reverse=True)
    return res


def calculate(src, rects):
    threshold = (rects[0][2] + rects[0][3]) / 2
    biggest_center = (rects[0][0] + rects[0][2] / 2, rects[0][1] + rects[0][3] / 2)
    centers = []
    for (x, y, w, h) in rects:
        # calculate the distance
        distance = ((x + w / 2) - biggest_center[0]) ** 2 + ((y + h / 2) - biggest_center[1]) ** 2
        distance = distance ** 0.5
        if distance < threshold:
            cv2.circle(src, (int(x + w / 2), int(y + h / 2)), 10, (0, 0, 255), -1)
            centers.append((x + w / 2, y + h / 2))
    cv2.imshow('src', src)

    # calculate the angle of the center of the biggest center
    if len(centers) > 1:
        angle = math.atan2(centers[1][1] - centers[0][1], centers[1][0] - centers[0][0])
        angle = angle * 180 / math.pi
        return angle


def detect(video_path):
    os.chdir(os.path.join(os.path.dirname(__file__), "./"))
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cur_state = 0
    count = 0
    while True:
        ret, frame = cap.read()
        rects = preprocess(frame)
        angle = calculate(frame, rects)
        if angle != None:
            if math.fabs(angle - cur_state) > 60:
                count +=1
                if count>40:
                    if -90 < angle <= -70:
                        print('A')
                    elif 40 <= angle <= 70:
                        print('B')
                    elif 120 < angle < 150:
                        print('C')
                    cur_state = angle
                    count = 0
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main():
    video_path = "demo.avi"
    detect(video_path)


if __name__ == '__main__':
    main()
