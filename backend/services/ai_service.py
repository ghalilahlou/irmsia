"""
Service d'analyse IA
Vision + LLM multimodal pour analyse médicale
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import base64
from PIL import Image

from backend.core.config import settings
from backend.models.dto import Finding, AIAnalysisResponse

logger = logging.getLogger(__name__)


class AIService:
    """Service d'analyse IA avec vision + LLM"""
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialise le modèle IA selon le provider"""
        if self.provider == "huggingface":
            self._init_huggingface()
        elif self.provider == "openai":
            self._init_openai()
        else:
            logger.info("Mode mock activé pour l'analyse IA")
    
    def _init_huggingface(self):
        """Initialise un modèle Hugging Face"""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            self.processor = BlipProcessor.from_pretrained(settings.HUGGINGFACE_MODEL)
            self.model = BlipForConditionalGeneration.from_pretrained(settings.HUGGINGFACE_MODEL)
            logger.info(f"Modèle Hugging Face chargé: {settings.HUGGINGFACE_MODEL}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle Hugging Face: {e}")
            logger.info("Basculement en mode mock")
            self.provider = "mock"
    
    def _init_openai(self):
        """Initialise l'API OpenAI"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY non configurée, basculement en mode mock")
            self.provider = "mock"
        else:
            try:
                import openai
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("Client OpenAI initialisé")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation OpenAI: {e}")
                self.provider = "mock"
    
    def analyze_image(
        self,
        image_path: str,
        modality: str = "MRI",
        additional_context: Optional[str] = None
    ) -> AIAnalysisResponse:
        """
        Analyse une image médicale
        
        Args:
            image_path: Chemin vers l'image PNG
            modality: Modalité d'imagerie (MRI, CT, X-Ray, etc.)
            additional_context: Contexte additionnel pour l'analyse
            
        Returns:
            Résultats de l'analyse
        """
        start_time = time.time()
        
        try:
            if self.provider == "mock":
                result = self._analyze_mock(image_path, modality, additional_context)
            elif self.provider == "huggingface":
                result = self._analyze_huggingface(image_path, modality, additional_context)
            elif self.provider == "openai":
                result = self._analyze_openai(image_path, modality, additional_context)
            else:
                result = self._analyze_mock(image_path, modality, additional_context)
            
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse IA: {e}")
            # Retourner un résultat d'erreur
            return AIAnalysisResponse(
                image_id="",
                findings=[],
                risk_score=0,
                suggested_diagnosis="Erreur lors de l'analyse",
                confidence=0.0,
                ai_model=self.provider,
                processing_time=time.time() - start_time,
                timestamp=time.time(),
                recommendations=["Vérification manuelle recommandée"]
            )
    
    def _analyze_mock(
        self,
        image_path: str,
        modality: str,
        additional_context: Optional[str]
    ) -> AIAnalysisResponse:
        """Analyse mock pour tests et développement"""
        import random
        
        # Simuler une analyse
        findings = [
            Finding(
                description="Aucune anomalie significative détectée",
                location="Global",
                confidence=0.85,
                severity="normal"
            )
        ]
        
        # Simuler un score de risque bas
        risk_score = random.randint(0, 20)
        
        # Diagnostic suggéré
        if risk_score < 10:
            diagnosis = "Examen normal, aucun signe pathologique évident"
        elif risk_score < 20:
            diagnosis = "Examen normal avec quelques variations anatomiques mineures"
        else:
            diagnosis = "Examen nécessitant une révision approfondie"
        
        return AIAnalysisResponse(
            image_id=Path(image_path).stem,
            findings=findings,
            risk_score=risk_score,
            suggested_diagnosis=diagnosis,
            confidence=0.75,
            ai_model="mock",
            processing_time=0.0,
            timestamp=datetime.now(),
            recommendations=[
                "Suivi standard selon protocole",
                "Comparaison avec examens antérieurs si disponibles"
            ]
        )
    
    def _analyze_huggingface(
        self,
        image_path: str,
        modality: str,
        additional_context: Optional[str]
    ) -> AIAnalysisResponse:
        """Analyse avec modèle Hugging Face"""
        
        try:
            # Charger l'image
            image = Image.open(image_path).convert("RGB")
            
            # Préparer le prompt
            prompt = f"Analyze this {modality} medical image. Describe any findings, abnormalities, or notable features."
            if additional_context:
                prompt += f" Context: {additional_context}"
            
            # Traiter l'image
            inputs = self.processor(image, prompt, return_tensors="pt")
            
            # Générer la description
            out = self.model.generate(**inputs, max_length=200)
            description = self.processor.decode(out[0], skip_special_tokens=True)
            
            # Parser la description en findings
            findings = [
                Finding(
                    description=description,
                    location="Global",
                    confidence=0.7,
                    severity="normal"
                )
            ]
            
            # Calculer un score de risque basique
            risk_keywords = ["abnormal", "lesion", "tumor", "mass", "pathology"]
            risk_score = sum(1 for keyword in risk_keywords if keyword.lower() in description.lower()) * 15
            risk_score = min(100, risk_score)
            
            return AIAnalysisResponse(
                image_id=Path(image_path).stem,
                findings=findings,
                risk_score=risk_score,
                suggested_diagnosis=description[:200],
                confidence=0.7,
                ai_model=settings.HUGGINGFACE_MODEL,
                processing_time=0.0,
                timestamp=datetime.now(),
                recommendations=["Révision par un radiologue recommandée"]
            )
            
        except Exception as e:
            logger.error(f"Erreur Hugging Face: {e}")
            return self._analyze_mock(image_path, modality, additional_context)
    
    def _analyze_openai(
        self,
        image_path: str,
        modality: str,
        additional_context: Optional[str]
    ) -> AIAnalysisResponse:
        """Analyse avec OpenAI Vision API"""
        
        try:
            # Encoder l'image en base64
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Préparer le prompt
            prompt = f"""Analyze this {modality} medical image and provide:
1. A detailed description of findings
2. Any abnormalities or notable features
3. A risk assessment (0-100)
4. A suggested radiological diagnosis
5. Recommendations

Format your response as JSON with: findings (array), risk_score (0-100), suggested_diagnosis, confidence (0-1), recommendations (array).
"""
            
            if additional_context:
                prompt += f"\n\nAdditional context: {additional_context}"
            
            # Appel API
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Parser la réponse
            result_text = response.choices[0].message.content
            
            # Essayer de parser JSON
            import json
            try:
                result_json = json.loads(result_text)
            except:
                # Si ce n'est pas du JSON, créer une réponse basique
                result_json = {
                    "findings": [{"description": result_text, "confidence": 0.8}],
                    "risk_score": 30,
                    "suggested_diagnosis": result_text[:200],
                    "confidence": 0.8,
                    "recommendations": ["Révision par un radiologue"]
                }
            
            findings = [
                Finding(
                    description=f.get("description", ""),
                    location=f.get("location"),
                    confidence=f.get("confidence", 0.8),
                    severity=f.get("severity", "normal")
                )
                for f in result_json.get("findings", [])
            ]
            
            return AIAnalysisResponse(
                image_id=Path(image_path).stem,
                findings=findings,
                risk_score=result_json.get("risk_score", 30),
                suggested_diagnosis=result_json.get("suggested_diagnosis", result_text[:200]),
                confidence=result_json.get("confidence", 0.8),
                ai_model=settings.OPENAI_MODEL,
                processing_time=0.0,
                timestamp=datetime.now(),
                recommendations=result_json.get("recommendations", [])
            )
            
        except Exception as e:
            logger.error(f"Erreur OpenAI: {e}")
            return self._analyze_mock(image_path, modality, additional_context)


# Instance globale
ai_service = AIService()

