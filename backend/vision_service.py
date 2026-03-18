import cv2, ollama
from ultralytics import YOLO

# load once at import time (downloads yolov8n.pt on first run)
yolo = YOLO("yolov8n.pt")


def preprocess(path: str):
    img = cv2.imread(path)
    img = cv2.resize(img, (640, 640))
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return img


def analyze_image(image_path: str) -> dict:
    img = preprocess(image_path)
    results = yolo.predict(img, conf=0.35, verbose=False)

    detections = []
    for r in results:
        for box in r.boxes:
            detections.append({
                "label": r.names[int(box.cls)],
                "confidence": round(float(box.conf), 3),
                "bbox": box.xyxy[0].tolist()
            })

    if not detections:
        diagnosis = "No components detected. Try a clearer image."
        return {"detections": [], "diagnosis": diagnosis}

    # describe detections to LLM
    det_str = "\n".join(
        f"- {d['label']} (confidence: {d['confidence']})"
        for d in detections
    )
    prompt = f"""You are an expert robotics engineer analyzing a machine image.

Detected components:
{det_str}

Based on these detections:
1. Identify what type of robot/machine this likely is
2. List any potential issues or maintenance concerns
3. Suggest any improvements or checks to perform"""

    resp = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "detections": detections,
        "diagnosis": resp["message"]["content"]
    }