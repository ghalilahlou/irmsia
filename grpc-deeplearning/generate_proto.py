"""
Script pour générer automatiquement les fichiers Protocol Buffer
"""

import subprocess
import sys
from pathlib import Path

def generate_proto_files():
    """Générer les fichiers Python depuis .proto"""
    
    proto_dir = Path(__file__).parent / 'proto'
    proto_file = proto_dir / 'irmsia_dicom.proto'
    
    if not proto_file.exists():
        print(f"❌ Proto file not found: {proto_file}")
        return False
    
    print("🔧 Generating Protocol Buffer files...")
    print(f"   Proto file: {proto_file}")
    
    # Command to generate Python files
    cmd = [
        sys.executable,
        '-m', 'grpc_tools.protoc',
        f'-I{proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        str(proto_file)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Protocol Buffer files generated successfully!")
        print(f"   {proto_dir / 'irmsia_dicom_pb2.py'}")
        print(f"   {proto_dir / 'irmsia_dicom_pb2_grpc.py'}")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating proto files:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ grpcio-tools not installed. Install with:")
        print("   pip install grpcio-tools")
        return False

if __name__ == '__main__':
    success = generate_proto_files()
    sys.exit(0 if success else 1)

