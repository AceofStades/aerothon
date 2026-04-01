import cv2 as cv

cap = cv.VideoCapture(0)
ret = True
while ret:
    ret, frame = cap.read()
    cv.imshow("webcam", frame)

    if cv.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
