"""
Training avec Dataset Organisé
Utilise les datasets restructurés pour un training optimal
"""

import sys
import io
from pathlib import Path
import torch
import json

# Fix Windows encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

from training.training_pipeline import TrainingPipeline, create_default_model

print("\n" + "="*70)
print("TRAINING AVEC DATASET ORGANISÉ")
print("="*70)

# Lister les datasets organisés disponibles
organized_dir = Path("datasets/organized")

if not organized_dir.exists():
    print(f"\n❌ Aucun dataset organisé trouvé")
    print(f"\n💡 Restructurez d'abord vos datasets:")
    print(f"   python auto_restructure_brain_mri.py")
    sys.exit(1)

# Trouver les datasets
datasets = [d for d in organized_dir.iterdir() if d.is_dir() and (d / "metadata.json").exists()]

if not datasets:
    print(f"\n❌ Aucun dataset organisé trouvé")
    print(f"\n💡 Restructurez d'abord vos datasets:")
    print(f"   python auto_restructure_brain_mri.py")
    sys.exit(1)

print(f"\n📂 Datasets disponibles:\n")

for i, dataset_dir in enumerate(datasets, 1):
    with open(dataset_dir / "metadata.json", 'r') as f:
        metadata = json.load(f)
    
    print(f"   {i}. {dataset_dir.name}")
    print(f"      Description: {metadata.get('description', 'N/A')}")
    print(f"      Images: {metadata['total_images']}")
    print(f"      Classes: {metadata['num_classes']}")
    print(f"      Train: {metadata['splits']['train']['total']}, Val: {metadata['splits']['val']['total']}, Test: {metadata['splits']['test']['total']}")
    print()

# Sélectionner le dataset
if len(datasets) == 1:
    choice = 1
    print(f"▶️  Utilisation automatique: {datasets[0].name}")
else:
    choice_input = input(f"Choisir un dataset (1-{len(datasets)}): ").strip()
    choice = int(choice_input) if choice_input.isdigit() else 1

selected_dataset = datasets[choice - 1]

# Charger metadata
with open(selected_dataset / "metadata.json", 'r') as f:
    metadata = json.load(f)

print(f"\n✅ Dataset sélectionné: {selected_dataset.name}")

# Configuration
splits_dir = selected_dataset / "splits"
train_csv = splits_dir / "train.csv"
val_csv = splits_dir / "val.csv"
test_csv = splits_dir / "test.csv"

# Vérifier que les fichiers existent
if not train_csv.exists():
    print(f"\n❌ Fichier train non trouvé: {train_csv}")
    sys.exit(1)

if not val_csv.exists():
    print(f"\n❌ Fichier val non trouvé: {val_csv}")
    sys.exit(1)

# Demander le nombre d'epochs
print(f"\n⚙️  Configuration du training:")
epochs_input = input(f"   Nombre d'epochs (défaut: 10): ").strip()
num_epochs = int(epochs_input) if epochs_input.isdigit() else 10

# Device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"   Device: {device}")
if device == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

# Créer le modèle
print(f"\n🧠 Création du modèle...")
num_classes = metadata['num_classes']
model = create_default_model(num_classes=num_classes)
print(f"   ✅ EfficientNet-B0 créé ({num_classes} classes)")

# Créer le pipeline
print(f"\n🚀 Initialisation du pipeline...")
output_name = f"training_{selected_dataset.name}"

pipeline = TrainingPipeline(
    model=model,
    train_csv=str(train_csv),
    val_csv=str(val_csv),
    output_dir=f'training_outputs/{output_name}',
    device=device
)

# Afficher statistiques
print(f"\n📊 Statistiques:")
print(f"   Train images: {metadata['splits']['train']['total']}")
print(f"   Val images: {metadata['splits']['val']['total']}")
print(f"   Classes: {', '.join(metadata['classes'])}")

# Distribution
train_split = metadata['splits']['train']
if 'tumor' in train_split:
    print(f"\n   Distribution Train:")
    print(f"      Tumeur: {train_split['tumor']}")
    print(f"      Sans tumeur: {train_split['no_tumor']}")

# Confirmation
print(f"\n" + "="*70)
print(f"🎯 PRÊT POUR LE TRAINING")
print("="*70)
print(f"\n   Epochs: {num_epochs}")
print(f"   Batch size: 32")
print(f"   Optimizer: AdamW (lr=1e-4)")
print(f"   Device: {device}")

# Temps estimé
if device == 'cuda':
    time_per_epoch = 2  # minutes with GPU
else:
    time_per_epoch = 15  # minutes with CPU

estimated_time = num_epochs * time_per_epoch

print(f"\n⏱️  Temps estimé: ~{estimated_time} minutes")

proceed = input(f"\n▶️  Lancer le training? (y/n): ").strip().lower()

if proceed != 'y':
    print(f"\n❌ Training annulé")
    sys.exit(0)

# Lancer le training
print(f"\n" + "="*70)
print(f"🚀 DÉMARRAGE DU TRAINING")
print("="*70 + "\n")

try:
    pipeline.train(
        num_epochs=num_epochs,
        early_stopping_patience=5
    )
    
    # Résultats
    print(f"\n" + "="*70)
    print(f"✅ TRAINING TERMINÉ!")
    print("="*70)
    
    history = pipeline.history
    
    print(f"\n📊 Résultats finaux:")
    print(f"   Train Loss: {history['train_loss'][-1]:.4f}")
    print(f"   Val Loss: {history['val_loss'][-1]:.4f}")
    print(f"   Train Acc: {history['train_acc'][-1]:.2f}%")
    print(f"   Val Acc: {history['val_acc'][-1]:.2f}%")
    
    # Meilleure epoch
    best_epoch = history['val_loss'].index(min(history['val_loss'])) + 1
    best_val_loss = min(history['val_loss'])
    best_val_acc = history['val_acc'][best_epoch - 1]
    
    print(f"\n🏆 Meilleure epoch: {best_epoch}")
    print(f"   Val Loss: {best_val_loss:.4f}")
    print(f"   Val Acc: {best_val_acc:.2f}%")
    
    print(f"\n📁 Modèles sauvegardés:")
    print(f"   {pipeline.run_dir}")
    print(f"   - best_model.pth")
    print(f"   - training_curves.png")
    print(f"   - training_history.json")
    
    # Analyse
    print(f"\n🔍 Analyse:")
    
    if best_val_acc > 80:
        print(f"   ✅ EXCELLENT - Accuracy > 80%")
    elif best_val_acc > 70:
        print(f"   ✅ BON - Accuracy > 70%")
    elif best_val_acc > 50:
        print(f"   ⚠️  MOYEN - Accuracy 50-70%")
    else:
        print(f"   ⚠️  FAIBLE - Accuracy < 50%")
    
    # Overfitting check
    gap = history['train_acc'][-1] - history['val_acc'][-1]
    
    if gap < 10:
        print(f"   ✅ Pas d'overfitting (gap: {gap:.1f}%)")
    elif gap < 20:
        print(f"   ⚠️  Léger overfitting (gap: {gap:.1f}%)")
    else:
        print(f"   ❌ Overfitting détecté (gap: {gap:.1f}%)")
    
    print(f"\n" + "="*70)
    print(f"🎉 SUCCÈS!")
    print("="*70)
    
except KeyboardInterrupt:
    print(f"\n\n⚠️  Training interrompu")
    print(f"   Progression sauvegardée: {pipeline.run_dir}")
    
except Exception as e:
    print(f"\n❌ Erreur:")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

