"""
Quick Test - Training Workflow
Test ultra-rapide (2 epochs) pour vérifier que tout fonctionne
"""

import sys
import io
from pathlib import Path
import torch

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

from training.training_pipeline import TrainingPipeline, create_default_model

print("\n" + "="*70)
print("QUICK TEST - TRAINING WORKFLOW (2 EPOCHS)")
print("="*70)

# Configuration
train_csv = 'datasets/brain_mri/splits/train.csv'
val_csv = 'datasets/brain_mri/splits/val.csv'

# Vérifier fichiers
if not Path(train_csv).exists():
    print(f"\n❌ Erreur: {train_csv} non trouvé")
    print(f"   Exécutez: python create_brain_mri_split.py")
    sys.exit(1)

print(f"\n✅ Fichiers trouvés")
print(f"   Train: {train_csv}")
print(f"   Val: {val_csv}")

# Device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\n💻 Device: {device}")
if device == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

# Créer modèle
print(f"\n🧠 Création du modèle...")
model = create_default_model(num_classes=2)
print(f"   ✅ EfficientNet-B0 créé")

# Pipeline
print(f"\n🚀 Initialisation du pipeline...")
pipeline = TrainingPipeline(
    model=model,
    train_csv=train_csv,
    val_csv=val_csv,
    output_dir='training_outputs/quick_test',
    device=device
)

print(f"\n" + "="*70)
print(f"🎯 TRAINING - 2 EPOCHS (Test Rapide)")
print(f"="*70)
print(f"\n⏱️  Temps estimé: 10-15 min (CPU) | 2-3 min (GPU)")
print(f"\n▶️  Démarrage...\n")

try:
    # Training
    pipeline.train(num_epochs=2, early_stopping_patience=5)
    
    # Résultats
    print(f"\n" + "="*70)
    print(f"✅ TRAINING TERMINÉ!")
    print(f"="*70)
    
    history = pipeline.history
    print(f"\n📊 Résultats:")
    print(f"   Train Loss: {history['train_loss'][-1]:.4f}")
    print(f"   Val Loss: {history['val_loss'][-1]:.4f}")
    print(f"   Train Acc: {history['train_acc'][-1]:.2f}%")
    print(f"   Val Acc: {history['val_acc'][-1]:.2f}%")
    
    print(f"\n✅ TEST RÉUSSI - Pipeline fonctionnel!")
    print(f"📁 Modèles: {pipeline.run_dir}")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n" + "="*70)

