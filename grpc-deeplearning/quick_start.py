"""
Script de démarrage rapide pour IRMSIA gRPC Deep Learning
"""

import sys
import subprocess
from pathlib import Path
import time

def print_banner():
    """Afficher le banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 IRMSIA gRPC Deep Learning - Quick Start                ║
║                                                              ║
║   Diagnostic DICOM avec IA et gRPC Optimisé                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Vérifier les dépendances"""
    print("\n📋 Checking requirements...")
    
    required_packages = [
        'grpc',
        'torch',
        'pydicom',
        'cv2',
        'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def generate_proto():
    """Générer les fichiers proto"""
    print("\n🔧 Generating Protocol Buffer files...")
    
    result = subprocess.run(
        [sys.executable, 'generate_proto.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✅ Proto files generated")
        return True
    else:
        print("   ❌ Failed to generate proto files")
        print(result.stderr)
        return False

def check_cuda():
    """Vérifier CUDA"""
    print("\n🎮 Checking GPU...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory // (1024**3)
            print(f"   ✅ GPU: {gpu_name} ({gpu_memory}GB)")
            return True
        else:
            print("   ⚠️  No GPU detected - will use CPU (slower)")
            return False
    except ImportError:
        print("   ❌ PyTorch not installed")
        return False

def start_server():
    """Démarrer le serveur"""
    print("\n🚀 Starting server...")
    print("   Press Ctrl+C to stop\n")
    
    try:
        subprocess.run(
            [sys.executable, 'server/diagnostic_server.py', '--port', '50051'],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")

def show_menu():
    """Afficher le menu"""
    print("\n" + "="*60)
    print("WHAT DO YOU WANT TO DO?")
    print("="*60)
    print("1. Start gRPC Server (Diagnostic Service)")
    print("2. Test Health Check")
    print("3. Test Simple Diagnosis")
    print("4. Test Streaming Diagnosis")
    print("5. Test Batch Diagnosis")
    print("6. Generate Proto Files Only")
    print("7. Exit")
    print("="*60)
    
    choice = input("\nYour choice [1-7]: ").strip()
    return choice

def test_health():
    """Tester le health check"""
    print("\n🏥 Testing health check...")
    
    result = subprocess.run(
        [sys.executable, 'client/diagnostic_client.py', '--health'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def test_simple_diagnosis():
    """Tester un diagnostic simple"""
    print("\n🔬 Testing simple diagnosis...")
    
    dicom_path = input("Enter DICOM file path: ").strip()
    
    if not Path(dicom_path).exists():
        print(f"❌ File not found: {dicom_path}")
        return
    
    result = subprocess.run(
        [sys.executable, 'client/diagnostic_client.py', '--dicom', dicom_path],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def test_streaming_diagnosis():
    """Tester un diagnostic streaming"""
    print("\n🔬 Testing streaming diagnosis...")
    
    dicom_path = input("Enter DICOM file path: ").strip()
    
    if not Path(dicom_path).exists():
        print(f"❌ File not found: {dicom_path}")
        return
    
    result = subprocess.run(
        [sys.executable, 'client/diagnostic_client.py', '--dicom', dicom_path, '--streaming'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def test_batch_diagnosis():
    """Tester un diagnostic batch"""
    print("\n🔬 Testing batch diagnosis...")
    
    print("Enter DICOM file paths (separated by space):")
    paths = input().strip().split()
    
    for path in paths:
        if not Path(path).exists():
            print(f"❌ File not found: {path}")
            return
    
    result = subprocess.run(
        [sys.executable, 'client/diagnostic_client.py', '--batch'] + paths,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def main():
    """Main function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install requirements first:")
        print("   pip install -r requirements.txt")
        return
    
    # Check proto files
    proto_dir = Path('proto')
    pb2_file = proto_dir / 'irmsia_dicom_pb2.py'
    
    if not pb2_file.exists():
        print("\n⚠️  Proto files not found")
        if not generate_proto():
            return
    
    # Check CUDA
    check_cuda()
    
    # Menu loop
    while True:
        choice = show_menu()
        
        if choice == '1':
            start_server()
        elif choice == '2':
            test_health()
        elif choice == '3':
            test_simple_diagnosis()
        elif choice == '4':
            test_streaming_diagnosis()
        elif choice == '5':
            test_batch_diagnosis()
        elif choice == '6':
            generate_proto()
        elif choice == '7':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice")
        
        if choice in ['2', '3', '4', '5', '6']:
            input("\n\nPress Enter to continue...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

