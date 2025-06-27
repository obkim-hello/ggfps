import os
import shutil

# Define structure
core_files = [
    'screen_capture.py', 'detection.py', 'automation.py', 'gui.py', '__init__.py'
]
training_files = ['annotator.py', 'trainer.py', '__init__.py']

# Create directories if missing
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

glfps_dir = 'glfps'
training_dir = os.path.join(glfps_dir, 'training')
ensure_dir(glfps_dir)
ensure_dir(training_dir)

# Move core files
for f in core_files:
    if os.path.exists(f):
        shutil.move(f, os.path.join(glfps_dir, f))
        print(f"Moved {f} -> {glfps_dir}/")
    elif os.path.exists(os.path.join(glfps_dir, f)):
        print(f"{f} already in {glfps_dir}/")

# Move training files
for f in training_files:
    src = f
    if os.path.exists(src):
        shutil.move(src, os.path.join(training_dir, f))
        print(f"Moved {f} -> {training_dir}/")
    elif os.path.exists(os.path.join(training_dir, f)):
        print(f"{f} already in {training_dir}/")

# Move training files from glfps/ to glfps/training/
for f in training_files:
    src = os.path.join(glfps_dir, f)
    if os.path.exists(src):
        shutil.move(src, os.path.join(training_dir, f))
        print(f"Moved {src} -> {training_dir}/")

# Ensure data, models, runs, venv are in root
for folder in ['data', 'models', 'runs', 'venv']:
    if os.path.exists(os.path.join(glfps_dir, folder)):
        shutil.move(os.path.join(glfps_dir, folder), folder)
        print(f"Moved {glfps_dir}/{folder} -> {folder}/")

print("\nReorganization complete. Please check your project structure.") 