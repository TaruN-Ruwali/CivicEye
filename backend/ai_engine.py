import cv2
import numpy as np

def verify_infrastructure_damage(image_file):
    try:
        # 1. load image
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None: return False, 0

        # 2. validation of road
        # texture
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # road will mostly be gray
        lower_gray = np.array([0, 0, 50])
        upper_gray = np.array([180, 50, 200])
        mask = cv2.inRange(hsv, lower_gray, upper_gray)
        road_pixel_ratio = np.sum(mask > 0) / mask.size

        # if < 30% , road rejected
        if road_pixel_ratio < 0.3:
            print(f"REJECTED: Not a road. Road Pixel Ratio: {road_pixel_ratio:.2f}")
            return False, 0

        # 3. analyze the damage on road
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 40, 120)

        # only focus on the road part for edges
        road_edges = cv2.bitwise_and(edges, mask)
        edge_density = np.sum(road_edges > 0) / np.sum(mask > 0)

        # 4. Final Score
        # Confidence score on how much messy texture on road
        confidence = min(edge_density * 15, 0.98)

        # if road has enough cracks/edges then accept it
        if edge_density > 0.015:
            return True, confidence
        else:
            return False, confidence

    except Exception as e:
        print(f"AI Error: {e}")
        return False, 0
