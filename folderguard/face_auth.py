import time
import cv2
import face_recognition

from . import config, security

def has_enrolled_face():
    return config.face_data_path().exists()

def enroll_face(samples=5, camera_index=0):
    cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    encodings = []

    while len(encodings) < samples:
        ok, frame = cam.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame)

        if len(locations) == 1:
            face_encoding = face_recognition.face_encodings(rgb_frame, locations)[0]
            encodings.append(face_encoding)
            print(f"Captured sample {len(encodings)}/{samples}")

        time.sleep(0.5)

    cam.release()
    security.save_encodings(config.face_data_path(), encodings)
    print("enrollment saved")
    return True

def verify_face(tolerance = 0.5, camera_index = 0):
    known_encodings = security.load_encodings(config.face_data_path())

    cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    ok, frame = cam.read()
    cam.release()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb_frame)

    if not locations:
        return False

    live_encoding = face_recognition.face_encodings(rgb_frame, locations)[0]
    distances = face_recognition.face_distance(known_encodings, live_encoding)

    return distances.min() <= tolerance

if __name__ == "__main__":
    result = verify_face()
    print("match:", result)