"""
Test Script - Data Pipeline
Script de test pour vérifier l'installation et le fonctionnement du pipeline
"""

import sys
from pathlib import Path
import logging
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_imports():
    """Tester les imports Python"""
    logger.info("Testing imports...")
    
    tests = {
        "PyTorch": lambda: __import__('torch'),
        "PyDICOM": lambda: __import__('pydicom'),
        "MONAI": lambda: __import__('monai'),
        "Pandas": lambda: __import__('pandas'),
        "NumPy": lambda: __import__('numpy'),
        "OpenCV": lambda: __import__('cv2'),
        "scikit-learn": lambda: __import__('sklearn'),
        "requests": lambda: __import__('requests'),
        "tqdm": lambda: __import__('tqdm'),
    }
    
    passed = 0
    failed = 0
    
    for name, import_func in tests.items():
        try:
            module = import_func()
            version = getattr(module, '__version__', 'N/A')
            logger.info(f"✅ {name}: {version}")
            passed += 1
        except ImportError as e:
            logger.error(f"❌ {name}: Import failed - {e}")
            failed += 1
    
    logger.info(f"\nImport Tests: {passed} passed, {failed} failed")
    return failed == 0


def test_collectors():
    """Tester les collectors"""
    logger.info("\nTesting collectors...")
    
    try:
        from collectors.tcia_collector import TCIACollector
        logger.info("✅ TCIA Collector imported")
        
        collector = TCIACollector(output_dir="datasets/test_tcia")
        logger.info("✅ TCIA Collector initialized")
        
    except Exception as e:
        logger.error(f"❌ TCIA Collector failed: {e}")
        return False
    
    try:
        from collectors.kaggle_collector import KaggleCollector
        logger.info("✅ Kaggle Collector imported")
        
        collector = KaggleCollector(output_dir="datasets/test_kaggle")
        logger.info("✅ Kaggle Collector initialized")
        
    except Exception as e:
        logger.error(f"❌ Kaggle Collector failed: {e}")
        return False
    
    try:
        from collectors.nih_collector import NIHCollector
        logger.info("✅ NIH Collector imported")
        
        collector = NIHCollector(output_dir="datasets/test_nih")
        logger.info("✅ NIH Collector initialized")
        
    except Exception as e:
        logger.error(f"❌ NIH Collector failed: {e}")
        return False
    
    return True


def test_dataset_manager():
    """Tester le dataset manager"""
    logger.info("\nTesting dataset manager...")
    
    try:
        from processors.dataset_manager import DatasetManager
        logger.info("✅ DatasetManager imported")
        
        manager = DatasetManager(base_dir="datasets/test")
        logger.info("✅ DatasetManager initialized")
        
        # Test summary
        manager.print_summary()
        logger.info("✅ DatasetManager summary works")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DatasetManager failed: {e}")
        return False


def test_training_pipeline():
    """Tester le training pipeline"""
    logger.info("\nTesting training pipeline...")
    
    try:
        from training.training_pipeline import create_default_model
        logger.info("✅ TrainingPipeline imported")
        
        # Créer un modèle simple
        model = create_default_model(num_classes=2)
        logger.info("✅ Default model created")
        
        # Vérifier le modèle
        import torch
        dummy_input = torch.randn(1, 1, 224, 224)
        output = model(dummy_input)
        logger.info(f"✅ Model forward pass works (output shape: {output.shape})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TrainingPipeline failed: {e}")
        return False


def test_cuda():
    """Tester CUDA availability"""
    logger.info("\nTesting CUDA...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            cuda_version = torch.version.cuda
            logger.info(f"✅ CUDA available")
            logger.info(f"   Device: {device_name}")
            logger.info(f"   CUDA Version: {cuda_version}")
            logger.info(f"   GPU Count: {torch.cuda.device_count()}")
            
            # Test simple computation
            x = torch.randn(10, 10).cuda()
            y = x @ x.T
            logger.info(f"✅ GPU computation works")
            
        else:
            logger.warning("⚠️  CUDA not available (CPU only)")
            logger.info("   Training will be slower on CPU")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CUDA test failed: {e}")
        return False


def test_file_structure():
    """Vérifier la structure des fichiers"""
    logger.info("\nTesting file structure...")
    
    required_files = [
        "collectors/tcia_collector.py",
        "collectors/kaggle_collector.py",
        "collectors/nih_collector.py",
        "processors/dataset_manager.py",
        "training/training_pipeline.py",
        "data_pipeline_orchestrator.py",
        "requirements.txt",
        "README.md",
        "QUICK_START.md",
        "DATASETS_SUMMARY.md",
        "PROJET_DATA_PIPELINE.md"
    ]
    
    missing = []
    
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            logger.info(f"✅ {file_path}")
        else:
            logger.error(f"❌ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        logger.error(f"\n❌ Missing {len(missing)} files")
        return False
    
    logger.info("\n✅ All required files present")
    return True


def test_kaggle_config():
    """Vérifier la configuration Kaggle"""
    logger.info("\nTesting Kaggle configuration...")
    
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    
    if kaggle_json.exists():
        logger.info("✅ Kaggle API key found")
        
        # Test Kaggle CLI
        try:
            import subprocess
            result = subprocess.run(
                ['kaggle', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Kaggle CLI works: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ Kaggle CLI failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("❌ Kaggle CLI not installed")
            logger.info("   Install with: pip install kaggle")
            return False
        except Exception as e:
            logger.error(f"❌ Kaggle CLI test failed: {e}")
            return False
    
    else:
        logger.warning("⚠️  Kaggle API key not configured")
        logger.info("   1. Go to: https://www.kaggle.com/account")
        logger.info("   2. Click 'Create New API Token'")
        logger.info(f"   3. Place kaggle.json in: {kaggle_json}")
        return False


def print_summary(results):
    """Afficher le résumé des tests"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-"*70)
    print(f"Total: {total} tests")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print("-"*70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Pipeline is ready to use!")
        print("\nNext steps:")
        print("1. Run the interactive menu:")
        print("   python data_pipeline_orchestrator.py")
        print("\n2. Or follow the Quick Start guide:")
        print("   See QUICK_START.md")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Configure Kaggle API (if using Kaggle)")
        print("3. Check CUDA installation (if using GPU)")
    
    print("="*70)
    
    return failed == 0


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("IRMSIA DATA PIPELINE - TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Run tests
    results["Imports"] = test_imports()
    results["File Structure"] = test_file_structure()
    results["Collectors"] = test_collectors()
    results["Dataset Manager"] = test_dataset_manager()
    results["Training Pipeline"] = test_training_pipeline()
    results["CUDA"] = test_cuda()
    results["Kaggle Config"] = test_kaggle_config()
    
    # Print summary
    success = print_summary(results)
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

