"""
Medical Report Generator
Generates comprehensive medical imaging reports with:
- Structured findings
- Visual annotations
- Measurements
- Recommendations
- Export to PDF/JSON
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """A single finding in the report"""
    id: int
    type: str
    location: str
    severity: str  # normal, mild, moderate, severe
    confidence: float
    description: str
    measurements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MedicalReport:
    """Complete medical imaging report"""
    # Header
    report_id: str
    generated_at: str
    image_id: str
    modality: str
    
    # Summary
    overall_assessment: str  # normal, abnormal, critical
    confidence_score: float
    
    # Findings
    findings: List[Finding] = field(default_factory=list)
    
    # Measurements
    measurements: Dict[str, Any] = field(default_factory=dict)
    
    # Visualizations
    visualizations: Dict[str, str] = field(default_factory=dict)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Technical details
    model_info: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class ReportGenerator:
    """
    Generates comprehensive medical reports from analysis results
    """
    
    SEVERITY_THRESHOLDS = {
        'normal': 0.3,
        'mild': 0.5,
        'moderate': 0.7,
        'severe': 0.85
    }
    
    RECOMMENDATIONS_BY_TYPE = {
        'tumor': [
            "Consultation oncologique recommandée",
            "IRM de contrôle dans 3 mois",
            "Biopsie peut être envisagée selon contexte clinique",
            "Comparaison avec examens antérieurs conseillée"
        ],
        'infection': [
            "Corrélation clinique et biologique recommandée",
            "Antibiothérapie selon antibiogramme",
            "Contrôle radiologique à 2 semaines",
            "Recherche de foyer infectieux primaire"
        ],
        'hemorrhage': [
            "Surveillance clinique rapprochée",
            "Contrôle d'imagerie à 24-48h recommandé",
            "Évaluation des paramètres de coagulation",
            "Consultation neurochirurgicale si indiquée"
        ],
        'fracture': [
            "Immobilisation selon localisation",
            "Consultation orthopédique recommandée",
            "Radiographies de contrôle à 6 semaines",
            "Évaluation du risque ostéoporotique"
        ],
        'edema': [
            "Recherche étiologique recommandée",
            "Traitement symptomatique selon cause",
            "Contrôle d'imagerie après traitement",
            "Évaluation cardio-rénale si généralisé"
        ],
        'normal': [
            "Aucune anomalie significative détectée",
            "Poursuite du suivi habituel",
            "Nouveau contrôle selon protocole standard"
        ],
        'default': [
            "Corrélation clinique recommandée",
            "Avis spécialisé si doute diagnostique",
            "Contrôle évolutif à discuter"
        ]
    }
    
    def __init__(self):
        self.report_counter = 0
    
    def generate_report(
        self,
        image_id: str,
        detection_result: Any,
        segmentation_result: Optional[Any] = None,
        visualizations: Optional[Dict[str, str]] = None,
        modality: str = "UNKNOWN",
        processing_time_ms: float = 0.0
    ) -> MedicalReport:
        """
        Generate a comprehensive medical report
        
        Args:
            image_id: Unique identifier for the image
            detection_result: Result from anomaly detection
            segmentation_result: Optional segmentation result
            visualizations: Base64-encoded visualization images
            modality: Imaging modality (CT, MRI, X-Ray, etc.)
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Complete MedicalReport
        """
        self.report_counter += 1
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.report_counter:04d}"
        
        # Determine overall assessment
        overall_assessment = self._determine_assessment(detection_result)
        
        # Generate findings
        findings = self._generate_findings(detection_result, segmentation_result)
        
        # Compile measurements
        measurements = self._compile_measurements(detection_result, segmentation_result)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(detection_result, findings)
        
        # Create report
        report = MedicalReport(
            report_id=report_id,
            generated_at=datetime.now().isoformat(),
            image_id=image_id,
            modality=modality,
            overall_assessment=overall_assessment,
            confidence_score=detection_result.confidence,
            findings=findings,
            measurements=measurements,
            visualizations=visualizations or {},
            recommendations=recommendations,
            model_info={
                "detection_backend": getattr(detection_result, 'metadata', {}).get('backend', 'unknown'),
                "version": "2.0.0"
            },
            processing_time_ms=processing_time_ms
        )
        
        logger.info(f"Generated report {report_id} for image {image_id}")
        return report
    
    def _determine_assessment(self, detection_result: Any) -> str:
        """Determine overall assessment"""
        if not detection_result.has_anomaly:
            return "normal"
        
        if detection_result.confidence > self.SEVERITY_THRESHOLDS['severe']:
            return "critical"
        elif detection_result.confidence > self.SEVERITY_THRESHOLDS['moderate']:
            return "abnormal"
        else:
            return "abnormal"
    
    def _generate_findings(
        self,
        detection_result: Any,
        segmentation_result: Optional[Any] = None
    ) -> List[Finding]:
        """Generate structured findings"""
        findings = []
        
        if not detection_result.has_anomaly:
            findings.append(Finding(
                id=1,
                type="normal",
                location="diffuse",
                severity="normal",
                confidence=detection_result.confidence,
                description="Aucune anomalie significative détectée. Aspect radiologique normal."
            ))
            return findings
        
        # Create findings from bounding boxes
        for i, box in enumerate(detection_result.bounding_boxes):
            severity = self._determine_severity(box.get('confidence', detection_result.confidence))
            
            # Determine location from coordinates
            location = self._determine_location(box)
            
            finding = Finding(
                id=i + 1,
                type=detection_result.anomaly_class,
                location=location,
                severity=severity,
                confidence=box.get('confidence', detection_result.confidence),
                description=self._generate_finding_description(
                    detection_result.anomaly_class,
                    severity,
                    location,
                    box
                ),
                measurements={
                    "width_px": box.get('width', 0),
                    "height_px": box.get('height', 0),
                    "area_px": box.get('area_pixels', box.get('width', 0) * box.get('height', 0)),
                }
            )
            
            # Add physical measurements if available
            if segmentation_result and segmentation_result.measurements:
                for region in segmentation_result.regions:
                    if region.get('id') == i + 1:
                        if 'area_mm2' in region:
                            finding.measurements['area_mm2'] = region['area_mm2']
                        if 'perimeter_mm' in region:
                            finding.measurements['perimeter_mm'] = region['perimeter_mm']
            
            findings.append(finding)
        
        return findings
    
    def _determine_severity(self, confidence: float) -> str:
        """Determine severity from confidence"""
        if confidence < self.SEVERITY_THRESHOLDS['normal']:
            return "normal"
        elif confidence < self.SEVERITY_THRESHOLDS['mild']:
            return "mild"
        elif confidence < self.SEVERITY_THRESHOLDS['moderate']:
            return "moderate"
        else:
            return "severe"
    
    def _determine_location(self, box: Dict) -> str:
        """Determine anatomical location from coordinates"""
        # This is a simplified version - would need actual anatomical mapping
        x = box.get('x', 0)
        y = box.get('y', 0)
        
        # Divide image into quadrants (assuming 512x512)
        if x < 256 and y < 256:
            return "supérieur gauche"
        elif x >= 256 and y < 256:
            return "supérieur droit"
        elif x < 256 and y >= 256:
            return "inférieur gauche"
        else:
            return "inférieur droit"
    
    def _generate_finding_description(
        self,
        anomaly_class: str,
        severity: str,
        location: str,
        box: Dict
    ) -> str:
        """Generate a descriptive text for a finding"""
        descriptions = {
            'tumor': f"Lésion suspecte d'aspect tumoral identifiée dans le quadrant {location}. "
                     f"Caractéristiques évocatrices d'un processus néoplasique de sévérité {severity}.",
            
            'infection': f"Foyer d'allure infectieuse localisé en {location}. "
                        f"Aspect compatible avec un processus inflammatoire/infectieux {severity}.",
            
            'hemorrhage': f"Plage hémorragique objectivée en {location}. "
                         f"Saignement de caractère {severity} nécessitant surveillance.",
            
            'fracture': f"Solution de continuité osseuse visualisée en {location}. "
                       f"Fracture de gravité {severity}.",
            
            'edema': f"Infiltration œdémateuse diffuse prédominant en {location}. "
                    f"Œdème de degré {severity}.",
            
            'other_anomaly': f"Anomalie non spécifique détectée en {location}. "
                            f"Corrélation clinique recommandée."
        }
        
        return descriptions.get(anomaly_class, descriptions['other_anomaly'])
    
    def _compile_measurements(
        self,
        detection_result: Any,
        segmentation_result: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Compile all measurements"""
        measurements = detection_result.measurements.copy() if detection_result.measurements else {}
        
        if segmentation_result and segmentation_result.measurements:
            measurements.update(segmentation_result.measurements)
        
        return measurements
    
    def _generate_recommendations(
        self,
        detection_result: Any,
        findings: List[Finding]
    ) -> List[str]:
        """Generate clinical recommendations"""
        if not detection_result.has_anomaly:
            return self.RECOMMENDATIONS_BY_TYPE['normal']
        
        anomaly_class = detection_result.anomaly_class
        recommendations = self.RECOMMENDATIONS_BY_TYPE.get(
            anomaly_class,
            self.RECOMMENDATIONS_BY_TYPE['default']
        )
        
        # Add severity-specific recommendations
        max_severity = max((f.severity for f in findings), default='normal')
        if max_severity in ['moderate', 'severe']:
            recommendations = [
                "⚠️ Anomalie significative nécessitant attention médicale prioritaire"
            ] + recommendations
        
        return recommendations
    
    def export_to_text(self, report: MedicalReport) -> str:
        """Export report to formatted text"""
        lines = [
            "=" * 80,
            "RAPPORT D'ANALYSE D'IMAGERIE MÉDICALE",
            "=" * 80,
            "",
            f"Numéro de rapport: {report.report_id}",
            f"Date de génération: {report.generated_at}",
            f"Image analysée: {report.image_id}",
            f"Modalité: {report.modality}",
            "",
            "-" * 40,
            "SYNTHÈSE",
            "-" * 40,
            f"Évaluation globale: {report.overall_assessment.upper()}",
            f"Score de confiance: {report.confidence_score*100:.1f}%",
            "",
            "-" * 40,
            "RÉSULTATS DÉTAILLÉS",
            "-" * 40,
        ]
        
        for finding in report.findings:
            lines.extend([
                "",
                f"Trouvaille #{finding.id}:",
                f"  Type: {finding.type}",
                f"  Localisation: {finding.location}",
                f"  Sévérité: {finding.severity}",
                f"  Confiance: {finding.confidence*100:.1f}%",
                f"  Description: {finding.description}",
            ])
            
            if finding.measurements:
                lines.append("  Mesures:")
                for key, value in finding.measurements.items():
                    if isinstance(value, float):
                        lines.append(f"    - {key}: {value:.2f}")
                    else:
                        lines.append(f"    - {key}: {value}")
        
        lines.extend([
            "",
            "-" * 40,
            "RECOMMANDATIONS",
            "-" * 40,
        ])
        
        for rec in report.recommendations:
            lines.append(f"• {rec}")
        
        lines.extend([
            "",
            "=" * 80,
            "Généré automatiquement par IRMSIA Deep Learning Analysis System",
            f"Version du modèle: {report.model_info.get('version', 'N/A')}",
            f"Temps de traitement: {report.processing_time_ms:.0f}ms",
            "=" * 80,
        ])
        
        return "\n".join(lines)


# Singleton
_generator_instance: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get singleton instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ReportGenerator()
    return _generator_instance

