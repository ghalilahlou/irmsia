"""
Training Pipeline pour Détecteur d'Anomalies
Entraînement semi-supervisé pour détection d'anomalies généraliste
"""

import sys
import io
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Import models
sys.path.insert(0, str(Path(__file__).parent))
from models.anomaly_detector import (
    SupervisedAnomalyClassifier,
    VariationalAutoencoder,
    HybridAnomalyDetector,
    ANOMALY_CLASSES
)

# Import dataset
from training.training_pipeline import DICOMDataset


class AnomalyTrainingPipeline:
    """
    Pipeline de training pour détection d'anomalies
    Gère training supervisé, non-supervisé et hybride
    """
    
    def __init__(
        self,
        train_csv: str,
        val_csv: str,
        output_dir: str = "training_outputs/anomaly_detection",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create run directory
        run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run_dir = self.output_dir / run_name
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.train_df = pd.read_csv(train_csv)
        self.val_df = pd.read_csv(val_csv)
        
        # Separate labeled and unlabeled
        self.train_labeled = self.train_df[self.train_df['is_labeled'] == 1]
        self.train_unlabeled = self.train_df[self.train_df['is_labeled'] == 0]
        
        print(f"\n📊 Données chargées:")
        print(f"   Train total: {len(self.train_df)}")
        print(f"      - Étiquetées: {len(self.train_labeled)}")
        print(f"      - Non-étiquetées: {len(self.train_unlabeled)}")
        print(f"   Val total: {len(self.val_df)}")
        
        # Create dataloaders (Windows: num_workers=0)
        import platform
        num_workers = 0 if platform.system() == 'Windows' else 4
        
        self.train_loader_all = DataLoader(
            DICOMDataset(train_csv),
            batch_size=16,
            shuffle=True,
            num_workers=num_workers
        )
        
        self.val_loader = DataLoader(
            DICOMDataset(val_csv),
            batch_size=16,
            shuffle=False,
            num_workers=num_workers
        )
        
        # Models (will be initialized per phase)
        self.supervised_model = None
        self.vae_model = None
        self.hybrid_model = None
        
        # History
        self.history = {
            'supervised': {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []},
            'unsupervised': {'train_loss': [], 'val_loss': []},
            'hybrid': {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
        }
    
    def train_supervised(self, num_epochs: int = 30):
        """
        Phase 1: Training supervisé sur données étiquetées
        """
        print(f"\n" + "="*70)
        print(f"PHASE 1: TRAINING SUPERVISÉ")
        print("="*70)
        
        print(f"\n🧠 Création du modèle supervisé...")
        self.supervised_model = SupervisedAnomalyClassifier(
            num_classes=len(ANOMALY_CLASSES)
        ).to(self.device)
        
        optimizer = torch.optim.AdamW(
            self.supervised_model.parameters(),
            lr=1e-4,
            weight_decay=1e-5
        )
        
        criterion = nn.CrossEntropyLoss()
        
        print(f"\n🚀 Entraînement sur données étiquetées...")
        print(f"   Epochs: {num_epochs}")
        
        # Create dataloader for labeled data only
        if len(self.train_labeled) > 0:
            # Save labeled CSV temporairement
            temp_csv = self.run_dir / "temp_labeled.csv"
            self.train_labeled.to_csv(temp_csv, index=False)
            
            labeled_loader = DataLoader(
                DICOMDataset(str(temp_csv)),
                batch_size=8,  # Reduced for memory
                shuffle=True,
                num_workers=0
            )
            
            best_val_loss = float('inf')
            
            for epoch in range(num_epochs):
                # Train
                self.supervised_model.train()
                train_loss = 0
                correct = 0
                total = 0
                
                for images, labels in tqdm(labeled_loader, desc=f"Epoch {epoch+1}/{num_epochs}"):
                    images = images.to(self.device)
                    labels = labels.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = self.supervised_model(images)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    
                    train_loss += loss.item()
                    _, predicted = outputs.max(1)
                    total += labels.size(0)
                    correct += predicted.eq(labels).sum().item()
                
                train_loss /= len(labeled_loader)
                train_acc = 100. * correct / total
                
                print(f"   Epoch {epoch+1}: Train Loss={train_loss:.4f}, Acc={train_acc:.2f}%")
                
                self.history['supervised']['train_loss'].append(train_loss)
                self.history['supervised']['train_acc'].append(train_acc)
                
                # Save best
                if train_loss < best_val_loss:
                    best_val_loss = train_loss
                    torch.save(
                        self.supervised_model.state_dict(),
                        self.run_dir / 'supervised_best.pth'
                    )
            
            temp_csv.unlink()  # Remove temp file
            
            print(f"\n✅ Training supervisé terminé")
            print(f"   Best Loss: {best_val_loss:.4f}")
        else:
            print(f"\n⚠️  Aucune donnée étiquetée disponible")
    
    def train_unsupervised(self, num_epochs: int = 50):
        """
        Phase 2: Training non-supervisé (VAE) sur données non-étiquetées
        """
        print(f"\n" + "="*70)
        print(f"PHASE 2: TRAINING NON-SUPERVISÉ (VAE)")
        print("="*70)
        
        print(f"\n🧠 Création du VAE...")
        self.vae_model = VariationalAutoencoder().to(self.device)
        
        optimizer = torch.optim.Adam(
            self.vae_model.parameters(),
            lr=1e-4
        )
        
        print(f"\n🚀 Entraînement sur données normales (non-étiquetées)...")
        print(f"   Epochs: {num_epochs}")
        
        # Use unlabeled data (assumed normal)
        if len(self.train_unlabeled) > 0:
            temp_csv = self.run_dir / "temp_unlabeled.csv"
            self.train_unlabeled.to_csv(temp_csv, index=False)
            
            unlabeled_loader = DataLoader(
                DICOMDataset(str(temp_csv)),
                batch_size=16,
                shuffle=True,
                num_workers=0
            )
            
            best_loss = float('inf')
            
            for epoch in range(num_epochs):
                self.vae_model.train()
                train_loss = 0
                
                for images, _ in tqdm(unlabeled_loader, desc=f"Epoch {epoch+1}/{num_epochs}"):
                    images = images.to(self.device)
                    
                    optimizer.zero_grad()
                    
                    # Forward
                    reconstruction, mu, logvar = self.vae_model(images)
                    
                    # VAE Loss
                    recon_loss = F.mse_loss(reconstruction, images)
                    kl_loss = -0.5 * torch.mean(
                        1 + logvar - mu.pow(2) - logvar.exp()
                    )
                    
                    loss = recon_loss + 0.1 * kl_loss
                    
                    loss.backward()
                    optimizer.step()
                    
                    train_loss += loss.item()
                
                train_loss /= len(unlabeled_loader)
                
                print(f"   Epoch {epoch+1}: Loss={train_loss:.4f}")
                
                self.history['unsupervised']['train_loss'].append(train_loss)
                
                # Save best
                if train_loss < best_loss:
                    best_loss = train_loss
                    torch.save(
                        self.vae_model.state_dict(),
                        self.run_dir / 'vae_best.pth'
                    )
            
            temp_csv.unlink()
            
            print(f"\n✅ Training VAE terminé")
            print(f"   Best Loss: {best_loss:.4f}")
        else:
            print(f"\n⚠️  Aucune donnée non-étiquetée disponible")
            print(f"   Utilisation de toutes les données pour VAE...")
            
            # Use all data
            self.train_unlabeled = self.train_df.copy()
            self.train_unsupervised(num_epochs)
    
    def train_hybrid(self, num_epochs: int = 30):
        """
        Phase 3: Training hybride (ensemble)
        """
        print(f"\n" + "="*70)
        print(f"PHASE 3: TRAINING HYBRIDE (ENSEMBLE)")
        print("="*70)
        
        print(f"\n🧠 Création du modèle hybride...")
        self.hybrid_model = HybridAnomalyDetector().to(self.device)
        
        # Load pretrained weights si disponibles
        if (self.run_dir / 'supervised_best.pth').exists():
            print(f"   ✅ Chargement du modèle supervisé pré-entraîné")
            self.hybrid_model.classifier.load_state_dict(
                torch.load(self.run_dir / 'supervised_best.pth')
            )
        
        if (self.run_dir / 'vae_best.pth').exists():
            print(f"   ✅ Chargement du VAE pré-entraîné")
            self.hybrid_model.vae.load_state_dict(
                torch.load(self.run_dir / 'vae_best.pth')
            )
        
        # Training ensemble
        print(f"\n🚀 Fine-tuning ensemble...")
        print(f"   Epochs: {num_epochs}")
        
        # À implémenter: logic de fine-tuning
        print(f"\n⚠️  Fine-tuning hybride: À implémenter")
        print(f"   Pour l'instant, utiliser les modèles pré-entraînés séparément")
        
        # Save combined model
        torch.save(
            self.hybrid_model.state_dict(),
            self.run_dir / 'hybrid_model.pth'
        )
        
        print(f"\n✅ Modèle hybride sauvegardé")
    
    def save_results(self):
        """Sauvegarder les résultats"""
        with open(self.run_dir / 'training_history.json', 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print(f"\n✅ Historique sauvegardé: {self.run_dir / 'training_history.json'}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Anomaly Detection Training')
    parser.add_argument('--train-csv', type=str, default='datasets/anomaly_detection/brain_mri/splits/train.csv')
    parser.add_argument('--val-csv', type=str, default='datasets/anomaly_detection/brain_mri/splits/val.csv')
    parser.add_argument('--phase', type=str, choices=['supervised', 'unsupervised', 'hybrid', 'all'], default='all')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--output', type=str, default='training_outputs/anomaly_detection')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("TRAINING - DÉTECTEUR D'ANOMALIES")
    print("="*70)
    
    # Vérifier fichiers
    if not Path(args.train_csv).exists():
        print(f"\n❌ Fichier train non trouvé: {args.train_csv}")
        print(f"\n💡 Exécutez d'abord:")
        print(f"   python auto_organize_anomaly_brain_mri.py")
        sys.exit(1)
    
    # Create pipeline
    pipeline = AnomalyTrainingPipeline(
        train_csv=args.train_csv,
        val_csv=args.val_csv,
        output_dir=args.output
    )
    
    # Training selon phase
    if args.phase == 'supervised' or args.phase == 'all':
        pipeline.train_supervised(num_epochs=args.epochs)
    
    if args.phase == 'unsupervised' or args.phase == 'all':
        pipeline.train_unsupervised(num_epochs=args.epochs)
    
    if args.phase == 'hybrid' or args.phase == 'all':
        pipeline.train_hybrid(num_epochs=args.epochs)
    
    # Save results
    pipeline.save_results()
    
    print(f"\n" + "="*70)
    print(f"✅ TRAINING TERMINÉ!")
    print("="*70)
    print(f"\n📁 Modèles sauvegardés: {pipeline.run_dir}")
    print(f"   - supervised_best.pth")
    print(f"   - vae_best.pth")
    print(f"   - hybrid_model.pth")


if __name__ == "__main__":
    main()

