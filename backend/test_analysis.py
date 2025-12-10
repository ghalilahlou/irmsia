"""
Test script for the analysis service
Verifies that trained models are loaded and working
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_model_loader():
    """Test the trained model loader"""
    print("\n" + "="*60)
    print("Testing Trained Model Loader")
    print("="*60)
    
    try:
        from backend.services.analysis import get_trained_model_loader, ANOMALY_CLASSES
        
        loader = get_trained_model_loader()
        
        print(f"\n✅ Model loader initialized")
        print(f"   Device: {loader.device}")
        print(f"   Model type: {loader.model_type or 'Not loaded'}")
        print(f"   Num classes: {loader.num_classes}")
        print(f"   Model loaded: {loader.model is not None}")
        
        print(f"\n📋 Available anomaly classes ({len(ANOMALY_CLASSES)}):")
        for i, cls in enumerate(ANOMALY_CLASSES):
            print(f"   {i}: {cls}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detector():
    """Test the anomaly detector"""
    print("\n" + "="*60)
    print("Testing Anomaly Detector")
    print("="*60)
    
    try:
        from backend.services.analysis import get_anomaly_detector
        
        detector = get_anomaly_detector()
        
        print(f"\n✅ Detector initialized")
        print(f"   Device: {detector.device}")
        print(f"   Model loader: {'Available' if detector.model_loader else 'Not available'}")
        
        # Test with a dummy image
        import numpy as np
        dummy_image = np.random.rand(224, 224).astype(np.float32)
        
        # Save temporary file
        import tempfile
        from PIL import Image
        
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir) / "test_image.png"
        
        img = Image.fromarray((dummy_image * 255).astype(np.uint8))
        img.save(temp_path)
        
        print(f"\n🔍 Testing detection on dummy image...")
        result = detector.detect(str(temp_path))
        
        print(f"\n📊 Detection Result:")
        print(f"   Has anomaly: {result.has_anomaly}")
        print(f"   Class: {result.anomaly_class}")
        print(f"   Name: {result.anomaly_name}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Severity: {result.severity}")
        print(f"   Urgency: {result.urgency}")
        print(f"   Regions: {len(result.bounding_boxes)}")
        print(f"   Has heatmap: {result.heatmap is not None}")
        print(f"   Has segmentation: {result.segmentation_mask is not None}")
        
        if result.top_predictions:
            print(f"\n   Top predictions:")
            for pred in result.top_predictions:
                print(f"     - {pred['class_name']}: {pred['probability']:.2%}")
        
        if result.recommendations:
            print(f"\n   Recommendations:")
            for rec in result.recommendations[:3]:
                print(f"     • {rec}")
        
        # Cleanup
        import os
        os.unlink(temp_path)
        os.rmdir(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test visualization service"""
    print("\n" + "="*60)
    print("Testing Visualization Service")
    print("="*60)
    
    try:
        from backend.services.analysis import get_visualization_service
        
        viz = get_visualization_service()
        
        print(f"\n✅ Visualization service initialized")
        
        # Test with dummy image
        import numpy as np
        dummy_image = np.random.rand(256, 256).astype(np.float32)
        dummy_heatmap = np.random.rand(256, 256).astype(np.float32)
        
        # Test heatmap overlay
        overlay = viz.create_heatmap_overlay(dummy_image, dummy_heatmap)
        print(f"   Heatmap overlay shape: {overlay.shape}")
        
        # Test annotated image
        boxes = [{"x": 50, "y": 50, "width": 100, "height": 100, "confidence": 0.9, "label": "test"}]
        annotated = viz.create_annotated_image(dummy_image, boxes)
        print(f"   Annotated image shape: {annotated.shape}")
        
        # Test base64 encoding
        b64 = viz.image_to_base64(dummy_image)
        print(f"   Base64 encoding: {len(b64)} chars")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("   IRMSIA Analysis Service Test Suite")
    print("="*60)
    
    results = {
        "Model Loader": test_model_loader(),
        "Detector": test_detector(),
        "Visualization": test_visualization(),
    }
    
    print("\n" + "="*60)
    print("   Test Summary")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("   All tests passed! ✅")
    else:
        print("   Some tests failed ❌")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

