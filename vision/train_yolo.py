# vision/train_yolo.py — fixed for Windows
from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO("yolov8n.pt")

    results = model.train(
        data=r"E:\ai_engineering_robotics_assistant_architecture\dataset\Arduino-esp-raspberryPI.v1i.yolov8\data.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        device=0,
        project="vision/runs",
        name="robotics_detector",
        exist_ok=True,
        patience=10,
        augment=True,
        workers=4,      # reduced from 8 — more stable on Windows
    )

    print(f"Training complete!")
    print(f"Best model: {results.save_dir}/weights/best.pt")