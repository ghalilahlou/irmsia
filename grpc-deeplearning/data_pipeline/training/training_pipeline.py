"""
Training Pipeline - Pipeline complet d'entraînement Deep Learning
Entraînement automatisé avec gestion de datasets, augmentation, et tracking
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from tqdm import tqdm
import pandas as pd
import pydicom
import numpy as np
from datetime import datetime
import json

from monai.transforms import (
    Compose, LoadImaged, EnsureChannelFirstd, Spacingd,
    ScaleIntensityRanged, RandRotated, RandFlipd, RandZoomd,
    RandGaussianNoised, RandAdjustContrastd, Resized
)
from monai.data import CacheDataset, DataLoader as MonaiDataLoader
from monai.networks.nets import EfficientNetBN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DICOMDataset(Dataset):
    """
    Dataset PyTorch pour fichiers DICOM et images médicales (TIFF, PNG, JPG)
    """
    
    def __init__(
        self,
        csv_file: str,
        transform=None,
        image_size: Tuple[int, int] = (224, 224),
        base_dir: str = "datasets"
    ):
        self.df = pd.read_csv(csv_file)
        self.transform = transform
        self.image_size = image_size
        self.base_dir = Path(base_dir)
        
        logger.info(f"Dataset loaded: {len(self.df)} images")
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # Get file path (relative to base_dir)
        img_path = self.base_dir / row['path']
        
        # Check file extension
        import os
        file_ext = os.path.splitext(str(img_path))[1].lower()
        
        img_path_str = str(img_path)
        from PIL import Image
        
        if file_ext in ['.dcm', '.dicom']:
            # Load DICOM
            dcm = pydicom.dcmread(img_path_str)
            img = dcm.pixel_array.astype(np.float32)
        elif file_ext in ['.tif', '.tiff', '.png', '.jpg', '.jpeg']:
            # Load image and convert to grayscale
            img_pil = Image.open(img_path_str)
            # Convert to grayscale if needed
            if img_pil.mode != 'L':
                img_pil = img_pil.convert('L')
            img = np.array(img_pil).astype(np.float32)
        else:
            raise ValueError(f"Unsupported file format: {file_ext} for file: {img_path_str}")
        
        # Normaliser
        img = (img - img.min()) / (img.max() - img.min() + 1e-8)
        
        # Resize
        import cv2
        img = cv2.resize(img, self.image_size)
        
        # Add channel dim
        img = np.expand_dims(img, axis=0)
        
        # Convert to tensor
        img_tensor = torch.from_numpy(img)
        
        # Apply transforms
        if self.transform:
            img_tensor = self.transform(img_tensor)
        
        # Get label
        label = 0  # Default
        if 'label' in row:
            label = int(row['label'])
        
        return img_tensor, label


class TrainingPipeline:
    """
    Pipeline d'entraînement complet
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_csv: str,
        val_csv: str,
        output_dir: str = "training_outputs",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.model = model.to(device)
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create run directory
        run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run_dir = self.output_dir / run_name
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        # Datasets
        self.train_dataset = DICOMDataset(train_csv)
        self.val_dataset = DICOMDataset(val_csv)
        
        # Dataloaders
        # Use num_workers=0 on Windows to avoid multiprocessing issues
        import platform
        num_workers = 0 if platform.system() == 'Windows' else 4
        use_pin_memory = device == 'cuda'
        
        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=32,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=use_pin_memory
        )
        
        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=32,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=use_pin_memory
        )
        
        # Optimizer & Loss
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=1e-4,
            weight_decay=1e-5
        )
        
        self.criterion = nn.CrossEntropyLoss()
        
        # Scheduler
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=50
        )
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
        
        logger.info(f"Training Pipeline initialized")
        logger.info(f"   Device: {self.device}")
        logger.info(f"   Train samples: {len(self.train_dataset)}")
        logger.info(f"   Val samples: {len(self.val_dataset)}")
        logger.info(f"   Output: {self.run_dir}")
    
    def train_epoch(self) -> Tuple[float, float]:
        """Entraîner une epoch"""
        self.model.train()
        
        total_loss = 0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc="Training")
        
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # Backward
            loss.backward()
            self.optimizer.step()
            
            # Metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': loss.item(),
                'acc': 100. * correct / total
            })
        
        epoch_loss = total_loss / len(self.train_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self) -> Tuple[float, float]:
        """Valider le modèle"""
        self.model.eval()
        
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in tqdm(self.val_loader, desc="Validation"):
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        val_loss = total_loss / len(self.val_loader)
        val_acc = 100. * correct / total
        
        return val_loss, val_acc
    
    def train(
        self,
        num_epochs: int = 50,
        early_stopping_patience: int = 10
    ):
        """
        Entraîner le modèle
        
        Args:
            num_epochs: Nombre d'epochs
            early_stopping_patience: Patience pour early stopping
        """
        logger.info(f"Starting training for {num_epochs} epochs...")
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(num_epochs):
            logger.info(f"\nEpoch {epoch+1}/{num_epochs}")
            
            # Train
            train_loss, train_acc = self.train_epoch()
            
            # Validate
            val_loss, val_acc = self.validate()
            
            # Update scheduler
            self.scheduler.step()
            
            # Log
            logger.info(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            logger.info(f"   Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                
                self.save_checkpoint('best_model.pth', epoch, val_loss, val_acc)
                logger.info(f"   ✅ Best model saved (Val Loss: {val_loss:.4f})")
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= early_stopping_patience:
                logger.info(f"Early stopping triggered after {epoch+1} epochs")
                break
            
            # Save checkpoint every 10 epochs
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth', epoch, val_loss, val_acc)
        
        # Save final model
        self.save_checkpoint('final_model.pth', num_epochs, val_loss, val_acc)
        
        # Save history
        self.save_history()
        
        logger.info(f"\n✅ Training completed!")
        logger.info(f"   Best Val Loss: {best_val_loss:.4f}")
        logger.info(f"   Models saved to: {self.run_dir}")
    
    def save_checkpoint(
        self,
        filename: str,
        epoch: int,
        val_loss: float,
        val_acc: float
    ):
        """Sauvegarder un checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'val_loss': val_loss,
            'val_acc': val_acc,
            'history': self.history
        }
        
        torch.save(checkpoint, self.run_dir / filename)
    
    def save_history(self):
        """Sauvegarder l'historique d'entraînement"""
        history_file = self.run_dir / 'training_history.json'
        
        with open(history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        logger.info(f"Training history saved: {history_file}")
        
        # Plot curves
        self.plot_training_curves()
    
    def plot_training_curves(self):
        """Tracer les courbes d'apprentissage"""
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # Loss
            ax1.plot(self.history['train_loss'], label='Train Loss')
            ax1.plot(self.history['val_loss'], label='Val Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.set_title('Training and Validation Loss')
            ax1.legend()
            ax1.grid(True)
            
            # Accuracy
            ax2.plot(self.history['train_acc'], label='Train Acc')
            ax2.plot(self.history['val_acc'], label='Val Acc')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Accuracy (%)')
            ax2.set_title('Training and Validation Accuracy')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            plt.savefig(self.run_dir / 'training_curves.png', dpi=300)
            
            logger.info(f"Training curves saved: {self.run_dir / 'training_curves.png'}")
        
        except ImportError:
            logger.warning("Matplotlib not installed. Skipping plot generation.")


def create_default_model(num_classes: int = 2) -> nn.Module:
    """
    Créer un modèle par défaut (EfficientNet-B0)
    
    Args:
        num_classes: Nombre de classes
    
    Returns:
        Model PyTorch
    """
    model = EfficientNetBN(
        model_name='efficientnet-b0',
        spatial_dims=2,
        in_channels=1,
        num_classes=num_classes,
        pretrained=False
    )
    
    return model


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Training Pipeline')
    parser.add_argument('--train-csv', type=str, required=True, help='Training CSV')
    parser.add_argument('--val-csv', type=str, required=True, help='Validation CSV')
    parser.add_argument('--num-classes', type=int, default=2, help='Number of classes')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--output', type=str, default='training_outputs', help='Output directory')
    
    args = parser.parse_args()
    
    # Create model
    model = create_default_model(num_classes=args.num_classes)
    
    # Create pipeline
    pipeline = TrainingPipeline(
        model=model,
        train_csv=args.train_csv,
        val_csv=args.val_csv,
        output_dir=args.output
    )
    
    # Train
    pipeline.train(num_epochs=args.epochs)

