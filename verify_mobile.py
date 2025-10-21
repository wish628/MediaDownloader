# Verification script for mobile app structure
import os

def verify_mobile_app():
    print("Verifying mobile app structure...")
    
    # Check required files
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
            print(f"❌ Missing file: {file}")
        else:
            print(f"✅ Found file: {file}")
    
    if missing_files:
        print(f"\nMissing {len(missing_files)} required files")
        return False
    
    # Check buildozer.spec configuration
    try:
        with open('buildozer.spec', 'r') as f:
            content = f.read()
            
            checks = [
                ('source.entrypoint = main_mobile.py', 'Entrypoint configured'),
                ('requirements = python3,kivy,requests,yt-dlp', 'Requirements configured'),
                ('icon.filename = icon.ico', 'Icon configured'),
                ('android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE', 'Permissions configured')
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
                    
    except Exception as e:
        print(f"❌ Error reading buildozer.spec: {e}")
        return False
    
    # Check requirements file
    try:
        with open('requirements_mobile.txt', 'r') as f:
            content = f.read().strip()
            required_deps = ['yt-dlp', 'kivy', 'requests']
            
            for dep in required_deps:
                if dep in content:
                    print(f"✅ Dependency {dep} found in requirements")
                else:
                    print(f"❌ Dependency {dep} missing from requirements")
                    
    except Exception as e:
        print(f"❌ Error reading requirements_mobile.txt: {e}")
        return False
    
    print("\n✅ Mobile app structure verification completed!")
    return True

if __name__ == "__main__":
    verify_mobile_app()