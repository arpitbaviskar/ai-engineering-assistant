from roboflow import Roboflow

rf = Roboflow(api_key="RGXpeohE6LdsIFpkTaMe")  # free at roboflow.com

# Electronics components dataset (already labeled, ~500 images)
project = rf.workspace("roboflow-universe-projects").project("electronic-components-plgbc")
version = project.version(1)
dataset = version.download("yolov8")

print(f"Dataset downloaded to: {dataset.location}")