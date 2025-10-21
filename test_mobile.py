# Simple test to verify the mobile app structure
import os

# Check if required files exist
required_files = [
    'main_mobile.py',
    'buildozer.spec',
    'requirements_mobile.txt',
    'icon.ico'
]

missing_files = []
for file in required_files:
    if not os.path.exists(file):
        missing_files.append(file)

if missing_files:
    print(f"Missing files: {missing_files}")
else:
    print("All required files are present!")

# Check buildozer.spec configuration
try:
    with open('buildozer.spec', 'r') as f:
        content = f.read()
        if 'source.entrypoint = main_mobile.py' in content:
            print("Buildozer entrypoint correctly configured")
        else:
            print("WARNING: Buildozer entrypoint may not be correctly configured")
            
        if 'requirements = python3,kivy,requests,yt-dlp' in content:
            print("Buildozer requirements correctly configured")
        else:
            print("WARNING: Buildozer requirements may not be correctly configured")
            
    print("Buildozer spec file check completed!")
except Exception as e:
    print(f"Error checking buildozer.spec: {e}")

print("Mobile app structure verification completed!")