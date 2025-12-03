"""
IRMSIA Data Pipeline
Pipeline complet pour télécharger, préparer et entraîner des modèles DL sur des datasets DICOM
"""

__version__ = "1.0.0"

from .collectors.tcia_collector import TCIACollector
from .collectors.kaggle_collector import KaggleCollector
from .collectors.nih_collector import NIHCollector
from .processors.dataset_manager import DatasetManager
from .training.training_pipeline import TrainingPipeline

__all__ = [
    'TCIACollector',
    'KaggleCollector',
    'NIHCollector',
    'DatasetManager',
    'TrainingPipeline'
]

