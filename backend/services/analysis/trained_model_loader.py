"""
Trained Model Loader
Loads trained models from grpc-deeplearning pipeline
Supports EfficientNet, VAE, and Hybrid models
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# Add grpc-deeplearning to path
GRPC_DL_PATH = Path(__file__).parent.parent.parent.parent / "grpc-deeplearning"
if str(GRPC_DL_PATH) not in sys.path:
    sys.path.insert(0, str(GRPC_DL_PATH))

# Model paths
TRAINED_MODELS_PATH = GRPC_DL_PATH / "data_pipeline" / "training_outputs"
ANOMALY_MODEL_PATH = TRAINED_MODELS_PATH / "anomaly_detection" / "run_20251203_103610" / "supervised_best.pth"
QUICK_TEST_MODEL_PATH = TRAINED_MODELS_PATH / "quick_test" / "run_20251203_094153" / "best_model.pth"


# Anomaly classes mapping (from training)
ANOMALY_CLASSES = [
    'normal',           # 0 - Pas d'anomalie
    'tumor',            # 1 - Tumeur / Masse suspecte
    'infection',        # 2 - Infection / Inflammation
    'hemorrhage',       # 3 - Hemorragie
    'fracture',         # 4 - Fracture
    'edema',            # 5 - Oedeme
    'atelectasis',      # 6 - Atelectasie pulmonaire
    'pneumothorax',     # 7 - Pneumothorax
    'consolidation',    # 8 - Consolidation pulmonaire
    'other_anomaly'     # 9 - Autre anomalie
]

# Descriptions detaillees des anomalies
ANOMALY_DESCRIPTIONS = {
    'normal': {
        'name': 'Normal',
        'description': 'Aucune anomalie detectee. Aspect radiologique dans les limites de la normale.',
        'severity': 'none',
        'urgency': 'routine',
        'recommendations': [
            'Poursuite du suivi habituel',
            'Pas d\'examen complementaire necessaire'
        ]
    },
    'tumor': {
        'name': 'Tumeur / Masse',
        'description': 'Lesion suspecte d\'aspect tumoral identifiee. Processus expansif necessitant caracterisation.',
        'severity': 'high',
        'urgency': 'urgent',
        'recommendations': [
            'Consultation oncologique recommandee',
            'IRM de caracterisation avec injection',
            'Biopsie a discuter selon contexte clinique',
            'Bilan d\'extension selon resultats'
        ]
    },
    'infection': {
        'name': 'Infection / Inflammation',
        'description': 'Foyer d\'allure infectieuse ou inflammatoire. Signes compatibles avec un processus infectieux.',
        'severity': 'moderate',
        'urgency': 'semi-urgent',
        'recommendations': [
            'Correlation clinique et biologique',
            'Prelevement bacteriologique si accessible',
            'Antibiotherapie adaptee',
            'Controle a 2 semaines'
        ]
    },
    'hemorrhage': {
        'name': 'Hemorragie',
        'description': 'Plage hemorragique objectivee. Saignement actif ou recent necessitant surveillance.',
        'severity': 'critical',
        'urgency': 'immediate',
        'recommendations': [
            'Surveillance rapprochee en USIC/Reanimation',
            'Controle d\'imagerie a 6-24h',
            'Bilan de coagulation',
            'Avis neurochirurgical/vasculaire selon localisation'
        ]
    },
    'fracture': {
        'name': 'Fracture',
        'description': 'Solution de continuite osseuse visualisee. Fracture necessitant prise en charge orthopedique.',
        'severity': 'moderate',
        'urgency': 'urgent',
        'recommendations': [
            'Immobilisation immediate',
            'Consultation orthopedique',
            'Radiographies complementaires selon localisation',
            'Evaluation du risque osteoporotique'
        ]
    },
    'edema': {
        'name': 'Oedeme',
        'description': 'Infiltration oedemateuse des tissus. Oedeme necessitant recherche etiologique.',
        'severity': 'moderate',
        'urgency': 'semi-urgent',
        'recommendations': [
            'Recherche de la cause sous-jacente',
            'Evaluation cardio-renale',
            'Traitement symptomatique',
            'Controle apres traitement'
        ]
    },
    'atelectasis': {
        'name': 'Atelectasie',
        'description': 'Collapsus pulmonaire partiel ou complet. Atelectasie necessitant exploration.',
        'severity': 'moderate',
        'urgency': 'semi-urgent',
        'recommendations': [
            'Fibroscopie bronchique si suspicion d\'obstruction',
            'Kinesitherapie respiratoire',
            'Recherche d\'une cause obstructive',
            'Controle radiologique'
        ]
    },
    'pneumothorax': {
        'name': 'Pneumothorax',
        'description': 'Epanchement gazeux pleural. Pneumothorax necessitant evaluation de la gravite.',
        'severity': 'high',
        'urgency': 'urgent',
        'recommendations': [
            'Evaluation de l\'importance (% de decollement)',
            'Drainage thoracique si > 20% ou symptomatique',
            'Surveillance si minime et asymptomatique',
            'Scanner thoracique si doute'
        ]
    },
    'consolidation': {
        'name': 'Consolidation pulmonaire',
        'description': 'Opacite alveolaire en faveur d\'une consolidation. Pneumopathie ou autre cause.',
        'severity': 'moderate',
        'urgency': 'semi-urgent',
        'recommendations': [
            'Correlation clinique',
            'Antibiotherapie probabiliste si infection',
            'Scanner si evolution defavorable',
            'Fibroscopie si suspicion de cancer'
        ]
    },
    'other_anomaly': {
        'name': 'Autre anomalie',
        'description': 'Anomalie non specifique detectee necessitant caracterisation complementaire.',
        'severity': 'low',
        'urgency': 'routine',
        'recommendations': [
            'Correlation clinique recommandee',
            'Avis specialise si doute diagnostique',
            'Controle evolutif a discuter'
        ]
    }
}


class TrainedModelLoader:
    """
    Loads and manages trained deep learning models
    """
    
    def __init__(self):
        self.model = None
        self.model_type = None
        self.device = "cpu"
        self.num_classes = 10
        self._initialize()
    
    def _initialize(self):
        """Initialize by detecting available models and PyTorch"""
        try:
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"PyTorch initialized on {self.device}")
            
            # Try to load trained model
            if self._load_trained_model():
                logger.info("Trained model loaded successfully")
            else:
                logger.warning("No trained model found, will use fallback")
                
        except ImportError as e:
            logger.warning(f"PyTorch not available: {e}")
    
    def _load_trained_model(self) -> bool:
        """Load the trained model from checkpoint"""
        import torch
        
        # Try anomaly detection model first
        model_paths = [
            ANOMALY_MODEL_PATH,
            QUICK_TEST_MODEL_PATH,
        ]
        
        for model_path in model_paths:
            if model_path.exists():
                try:
                    logger.info(f"Loading model from {model_path}")
                    
                    # Load checkpoint
                    checkpoint = torch.load(model_path, map_location=self.device)
                    
                    # Determine model architecture
                    if 'model_state_dict' in checkpoint:
                        state_dict = checkpoint['model_state_dict']
                    else:
                        state_dict = checkpoint
                    
                    # Create model based on state_dict structure
                    self.model = self._create_model_from_state_dict(state_dict)
                    
                    if self.model:
                        self.model.load_state_dict(state_dict, strict=False)
                        self.model = self.model.to(self.device)
                        self.model.eval()
                        self.model_type = "trained_efficientnet"
                        
                        logger.info(f"Model loaded: {model_path.name}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Failed to load {model_path}: {e}")
        
        return False
    
    def _create_model_from_state_dict(self, state_dict: Dict):
        """Create model architecture from state dict keys"""
        try:
            from monai.networks.nets import EfficientNetBN
            
            # Detect number of classes from final layer
            for key in state_dict.keys():
                if 'classifier' in key or '_fc' in key:
                    if 'weight' in key:
                        self.num_classes = state_dict[key].shape[0]
                        break
            
            # Create EfficientNet model
            model = EfficientNetBN(
                model_name='efficientnet-b0',
                spatial_dims=2,
                in_channels=1,
                num_classes=self.num_classes,
                pretrained=False
            )
            
            logger.info(f"Created EfficientNet model with {self.num_classes} classes")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            return None
    
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Run prediction on an image
        
        Args:
            image: Numpy array (H, W) or (C, H, W)
            
        Returns:
            Dict with predictions
        """
        if self.model is None:
            return self._fallback_prediction(image)
        
        import torch
        import torch.nn.functional as F
        
        # Preprocess image
        img_tensor = self._preprocess_image(image)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = F.softmax(outputs, dim=1)
            
            # Get top predictions
            top_probs, top_indices = torch.topk(probs, k=min(3, self.num_classes), dim=1)
        
        # Extract results
        predicted_class = top_indices[0, 0].item()
        confidence = top_probs[0, 0].item()
        
        # Get class name
        class_name = ANOMALY_CLASSES[predicted_class] if predicted_class < len(ANOMALY_CLASSES) else 'other_anomaly'
        
        # Get anomaly info
        anomaly_info = ANOMALY_DESCRIPTIONS.get(class_name, ANOMALY_DESCRIPTIONS['other_anomaly'])
        
        # Build predictions list
        predictions = []
        for i in range(min(3, self.num_classes)):
            idx = top_indices[0, i].item()
            prob = top_probs[0, i].item()
            name = ANOMALY_CLASSES[idx] if idx < len(ANOMALY_CLASSES) else 'other_anomaly'
            predictions.append({
                'class_id': idx,
                'class_name': name,
                'probability': float(prob)
            })
        
        return {
            'has_anomaly': class_name != 'normal',
            'anomaly_class': class_name,
            'anomaly_name': anomaly_info['name'],
            'confidence': float(confidence),
            'severity': anomaly_info['severity'],
            'urgency': anomaly_info['urgency'],
            'description': anomaly_info['description'],
            'recommendations': anomaly_info['recommendations'],
            'top_predictions': predictions,
            'model_type': self.model_type or 'fallback',
            'raw_outputs': outputs[0].cpu().numpy().tolist() if self.model else None
        }
    
    def _preprocess_image(self, image: np.ndarray):
        """Preprocess image for model input"""
        import torch
        import cv2
        
        # Ensure 2D
        if len(image.shape) == 3:
            if image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                image = image[:, :, 0]
        
        # Normalize
        image = image.astype(np.float32)
        if image.max() > 1:
            image = (image - image.min()) / (image.max() - image.min() + 1e-8)
        
        # Resize to 224x224
        image = cv2.resize(image, (224, 224))
        
        # Add batch and channel dimensions
        img_tensor = torch.from_numpy(image).unsqueeze(0).unsqueeze(0)
        
        return img_tensor.to(self.device)
    
    def _fallback_prediction(self, image: np.ndarray) -> Dict[str, Any]:
        """Fallback prediction using image analysis"""
        import cv2
        
        # Simple analysis
        if image.max() > 1:
            image = (image - image.min()) / (image.max() - image.min() + 1e-8)
        
        # Calculate intensity statistics
        mean_intensity = float(np.mean(image))
        std_intensity = float(np.std(image))
        
        # Edge detection for structural analysis
        edges = cv2.Canny((image * 255).astype(np.uint8), 50, 150)
        edge_density = float(np.sum(edges > 0) / edges.size)
        
        # Heuristic classification
        has_anomaly = edge_density > 0.05 or std_intensity > 0.2
        
        return {
            'has_anomaly': has_anomaly,
            'anomaly_class': 'other_anomaly' if has_anomaly else 'normal',
            'anomaly_name': 'Anomalie detectee' if has_anomaly else 'Normal',
            'confidence': 0.5 if has_anomaly else 0.8,
            'severity': 'low' if has_anomaly else 'none',
            'urgency': 'routine',
            'description': ANOMALY_DESCRIPTIONS['other_anomaly' if has_anomaly else 'normal']['description'],
            'recommendations': ANOMALY_DESCRIPTIONS['other_anomaly' if has_anomaly else 'normal']['recommendations'],
            'top_predictions': [{
                'class_id': 9 if has_anomaly else 0,
                'class_name': 'other_anomaly' if has_anomaly else 'normal',
                'probability': 0.5 if has_anomaly else 0.8
            }],
            'model_type': 'fallback_heuristic',
            'raw_outputs': None
        }
    
    def generate_gradcam(self, image: np.ndarray, target_class: Optional[int] = None) -> Optional[np.ndarray]:
        """
        Generate GradCAM visualization
        
        Args:
            image: Input image
            target_class: Target class for GradCAM (None = predicted class)
            
        Returns:
            GradCAM heatmap as numpy array
        """
        if self.model is None:
            return None
        
        try:
            import torch
            from pytorch_grad_cam import GradCAM
            from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
            
            # Prepare image
            img_tensor = self._preprocess_image(image)
            img_tensor.requires_grad = True
            
            # Find target layer
            target_layers = []
            for name, module in self.model.named_modules():
                if 'blocks' in name or 'features' in name:
                    if isinstance(module, torch.nn.Conv2d):
                        target_layers.append(module)
            
            if not target_layers:
                logger.warning("No suitable layers found for GradCAM")
                return None
            
            # Use last conv layer
            target_layer = [target_layers[-1]]
            
            # Create GradCAM
            cam = GradCAM(model=self.model, target_layers=target_layer)
            
            # Generate
            targets = [ClassifierOutputTarget(target_class)] if target_class is not None else None
            grayscale_cam = cam(input_tensor=img_tensor, targets=targets)
            
            return grayscale_cam[0]
            
        except Exception as e:
            logger.warning(f"GradCAM generation failed: {e}")
            return None


# Singleton instance
_loader_instance: Optional[TrainedModelLoader] = None


def get_trained_model_loader() -> TrainedModelLoader:
    """Get singleton instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = TrainedModelLoader()
    return _loader_instance


# Export anomaly info
def get_anomaly_info(class_name: str) -> Dict[str, Any]:
    """Get detailed info for an anomaly class"""
    return ANOMALY_DESCRIPTIONS.get(class_name, ANOMALY_DESCRIPTIONS['other_anomaly'])


def get_all_anomaly_classes() -> list:
    """Get list of all anomaly classes"""
    return ANOMALY_CLASSES.copy()

