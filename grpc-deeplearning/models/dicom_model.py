"""
Modèle Deep Learning optimisé pour diagnostic DICOM
Architecture: EfficientNet-B4 + Attention + Multi-Head Classification
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import timm
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AttentionBlock(nn.Module):
    """Attention mechanism pour focus sur régions importantes"""
    
    def __init__(self, in_channels: int):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // 8, 1),
            nn.BatchNorm2d(in_channels // 8),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // 8, in_channels, 1),
            nn.BatchNorm2d(in_channels),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        attention_weights = self.attention(x)
        return x * attention_weights


class MultiHeadDiagnosticModel(nn.Module):
    """
    Modèle multi-tête pour diagnostic DICOM
    - Classification principale (Normal/Abnormal)
    - Détection de pathologies multiples
    - Prédiction de sévérité
    - Évaluation de risque
    """
    
    def __init__(
        self,
        num_classes: int = 5,
        num_pathologies: int = 15,
        backbone: str = 'efficientnet_b4',
        pretrained: bool = True,
        use_attention: bool = True
    ):
        super().__init__()
        
        self.num_classes = num_classes
        self.num_pathologies = num_pathologies
        self.use_attention = use_attention
        
        # Backbone: EfficientNet-B4 (bon compromis vitesse/précision)
        logger.info(f"Loading backbone: {backbone}")
        self.backbone = timm.create_model(
            backbone,
            pretrained=pretrained,
            in_chans=1,  # Grayscale medical images
            num_classes=0,  # Remove classification head
            global_pool=''  # Remove global pooling
        )
        
        # Feature dimensions
        self.feature_dim = self.backbone.num_features
        logger.info(f"Feature dimension: {self.feature_dim}")
        
        # Attention module (optionnel)
        if use_attention:
            self.attention = AttentionBlock(self.feature_dim)
        
        # Global pooling
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        
        # Classification heads
        
        # 1. Primary classification (Normal vs Abnormal)
        self.primary_classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(self.feature_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, num_classes)
        )
        
        # 2. Pathology detection (multi-label)
        self.pathology_detector = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(self.feature_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, num_pathologies)
        )
        
        # 3. Severity predictor
        self.severity_predictor = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(self.feature_dim, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 6)  # 6 severity levels
        )
        
        # 4. Risk score regressor
        self.risk_regressor = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(self.feature_dim, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()  # Output [0, 1]
        )
        
        logger.info(f"Model initialized: {self.__class__.__name__}")
        logger.info(f"Total parameters: {sum(p.numel() for p in self.parameters())/1e6:.2f}M")
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input tensor [B, 1, H, W]
        
        Returns:
            Dict with predictions:
                - primary: [B, num_classes]
                - pathologies: [B, num_pathologies]
                - severity: [B, 6]
                - risk_score: [B, 1]
                - features: [B, feature_dim] (pour Grad-CAM)
        """
        # Extract features
        features = self.backbone(x)  # [B, C, H', W']
        
        # Apply attention
        if self.use_attention:
            features = self.attention(features)
        
        # Global pooling
        pooled_features = self.global_pool(features).flatten(1)  # [B, C]
        
        # Multiple predictions
        outputs = {
            'primary': self.primary_classifier(pooled_features),
            'pathologies': self.pathology_detector(pooled_features),
            'severity': self.severity_predictor(pooled_features),
            'risk_score': self.risk_regressor(pooled_features),
            'features': pooled_features,  # Pour Grad-CAM
            'feature_maps': features  # Pour visualisation
        }
        
        return outputs
    
    def predict(self, x: torch.Tensor) -> Dict[str, any]:
        """
        Prédiction avec post-traitement
        
        Returns:
            Dict avec résultats lisibles:
                - primary_class: int
                - primary_confidence: float
                - detected_pathologies: List[Tuple[str, float]]
                - severity_level: int
                - risk_score: float (0-100)
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
        
        # Primary classification
        primary_probs = F.softmax(outputs['primary'], dim=1)
        primary_class = primary_probs.argmax(dim=1).item()
        primary_confidence = primary_probs.max(dim=1).values.item()
        
        # Pathologies (multi-label)
        pathology_probs = torch.sigmoid(outputs['pathologies'])
        detected_pathologies = []
        for i, prob in enumerate(pathology_probs[0]):
            if prob > 0.5:  # Threshold
                detected_pathologies.append((i, prob.item()))
        
        # Severity
        severity_probs = F.softmax(outputs['severity'], dim=1)
        severity_level = severity_probs.argmax(dim=1).item()
        
        # Risk score (0-100)
        risk_score = outputs['risk_score'].item() * 100
        
        return {
            'primary_class': primary_class,
            'primary_confidence': primary_confidence,
            'primary_probs': primary_probs[0].cpu().numpy(),
            'detected_pathologies': detected_pathologies,
            'severity_level': severity_level,
            'severity_confidence': severity_probs.max(dim=1).values.item(),
            'risk_score': risk_score
        }


class SegmentationModel(nn.Module):
    """
    U-Net pour segmentation de lésions/tumeurs
    """
    
    def __init__(self, in_channels: int = 1, out_channels: int = 1):
        super().__init__()
        
        # Encoder
        self.enc1 = self.conv_block(in_channels, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)
        self.enc4 = self.conv_block(256, 512)
        
        # Bottleneck
        self.bottleneck = self.conv_block(512, 1024)
        
        # Decoder
        self.upconv4 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.dec4 = self.conv_block(1024, 512)
        self.upconv3 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec3 = self.conv_block(512, 256)
        self.upconv2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec2 = self.conv_block(256, 128)
        self.upconv1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.dec1 = self.conv_block(128, 64)
        
        # Output
        self.out = nn.Conv2d(64, out_channels, 1)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
    
    def conv_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))
        
        # Bottleneck
        bottleneck = self.bottleneck(self.pool(enc4))
        
        # Decoder with skip connections
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat([dec4, enc4], dim=1)
        dec4 = self.dec4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat([dec3, enc3], dim=1)
        dec3 = self.dec3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat([dec2, enc2], dim=1)
        dec2 = self.dec2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat([dec1, enc1], dim=1)
        dec1 = self.dec1(dec1)
        
        # Output
        out = torch.sigmoid(self.out(dec1))
        
        return out


class DiagnosticPipeline:
    """
    Pipeline complet de diagnostic
    Combine classification + segmentation + Grad-CAM
    """
    
    def __init__(
        self,
        device: str = 'cuda',
        classification_model_path: Optional[str] = None,
        segmentation_model_path: Optional[str] = None
    ):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Load classification model
        self.classification_model = MultiHeadDiagnosticModel(
            num_classes=5,
            num_pathologies=15,
            backbone='efficientnet_b4',
            pretrained=True,
            use_attention=True
        ).to(self.device)
        
        if classification_model_path:
            logger.info(f"Loading classification weights from {classification_model_path}")
            self.classification_model.load_state_dict(
                torch.load(classification_model_path, map_location=self.device)
            )
        
        self.classification_model.eval()
        
        # Load segmentation model
        self.segmentation_model = SegmentationModel(
            in_channels=1,
            out_channels=1
        ).to(self.device)
        
        if segmentation_model_path:
            logger.info(f"Loading segmentation weights from {segmentation_model_path}")
            self.segmentation_model.load_state_dict(
                torch.load(segmentation_model_path, map_location=self.device)
            )
        
        self.segmentation_model.eval()
        
        logger.info("Diagnostic pipeline ready")
    
    @torch.no_grad()
    def predict(
        self,
        image: torch.Tensor,
        include_segmentation: bool = False,
        include_gradcam: bool = False
    ) -> Dict:
        """
        Prédiction complète
        
        Args:
            image: Tensor [1, 1, H, W] ou [1, H, W]
            include_segmentation: Inclure la segmentation
            include_gradcam: Inclure Grad-CAM
        
        Returns:
            Dict avec tous les résultats
        """
        if image.dim() == 3:
            image = image.unsqueeze(0)  # Add batch dimension
        
        image = image.to(self.device)
        
        # Classification
        classification_results = self.classification_model.predict(image)
        
        results = {
            'classification': classification_results,
            'segmentation': None,
            'gradcam': None
        }
        
        # Segmentation (optionnel)
        if include_segmentation:
            segmentation_mask = self.segmentation_model(image)
            results['segmentation'] = segmentation_mask.cpu()
        
        # Grad-CAM (optionnel)
        if include_gradcam:
            gradcam = self.generate_gradcam(image)
            results['gradcam'] = gradcam
        
        return results
    
    def generate_gradcam(self, image: torch.Tensor) -> torch.Tensor:
        """
        Génère une heatmap Grad-CAM pour explicabilité
        
        Returns:
            Heatmap [1, H, W]
        """
        # Simplified Grad-CAM
        self.classification_model.eval()
        
        # Forward pass
        outputs = self.classification_model(image)
        features = outputs['feature_maps']  # [1, C, H', W']
        
        # Get prediction
        pred_class = outputs['primary'].argmax(dim=1)
        
        # Backward to get gradients
        self.classification_model.zero_grad()
        class_score = outputs['primary'][0, pred_class]
        class_score.backward()
        
        # Get gradients
        gradients = features.grad  # [1, C, H', W']
        
        # Global average pooling of gradients
        weights = gradients.mean(dim=(2, 3), keepdim=True)  # [1, C, 1, 1]
        
        # Weighted combination
        cam = (weights * features).sum(dim=1, keepdim=True)  # [1, 1, H', W']
        cam = F.relu(cam)  # ReLU
        
        # Normalize
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        
        # Resize to original image size
        cam = F.interpolate(
            cam,
            size=image.shape[2:],
            mode='bilinear',
            align_corners=False
        )
        
        return cam.cpu()
    
    def warmup(self, input_size: Tuple[int, int] = (512, 512)):
        """Warmup GPU pour des inférences plus rapides"""
        logger.info("Warming up models...")
        dummy_input = torch.randn(1, 1, *input_size).to(self.device)
        
        # Warmup classification
        for _ in range(3):
            _ = self.classification_model(dummy_input)
        
        # Warmup segmentation
        for _ in range(3):
            _ = self.segmentation_model(dummy_input)
        
        logger.info("Warmup complete")


# Pathology classes (15 pathologies communes)
PATHOLOGY_CLASSES = [
    "brain_tumor",
    "stroke_ischemic",
    "stroke_hemorrhagic",
    "multiple_sclerosis",
    "lung_nodule",
    "pneumonia",
    "covid19",
    "pleural_effusion",
    "fracture",
    "osteoarthritis",
    "disc_herniation",
    "kidney_stone",
    "liver_lesion",
    "aortic_aneurysm",
    "lymphadenopathy"
]

# Primary classes
PRIMARY_CLASSES = [
    "normal",
    "abnormal_mild",
    "abnormal_moderate",
    "abnormal_severe",
    "abnormal_critical"
]

# Severity levels
SEVERITY_LEVELS = [
    "normal",
    "minimal",
    "mild",
    "moderate",
    "severe",
    "critical"
]


if __name__ == "__main__":
    # Test model
    logging.basicConfig(level=logging.INFO)
    
    model = MultiHeadDiagnosticModel(
        num_classes=5,
        num_pathologies=15,
        backbone='efficientnet_b4',
        pretrained=False
    )
    
    # Test input
    x = torch.randn(2, 1, 512, 512)
    outputs = model(x)
    
    print("Output shapes:")
    for key, value in outputs.items():
        if isinstance(value, torch.Tensor):
            print(f"  {key}: {value.shape}")
    
    # Test prediction
    prediction = model.predict(x[:1])
    print("\nPrediction:")
    for key, value in prediction.items():
        print(f"  {key}: {value}")

