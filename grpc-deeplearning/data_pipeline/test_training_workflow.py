"""
Test Training Workflow - Brain MRI Dataset
Script de test pour valider le pipeline d'entraînement complet
"""

import sys
import io
from pathlib import Path
import logging
import torch
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import du training pipeline
from training.training_pipeline import TrainingPipeline, create_default_model


def test_training_workflow():
    """
    Test complet du workflow d'entraînement
    """
    
    print("\n" + "="*70)
    print("TEST TRAINING WORKFLOW - BRAIN MRI DATASET")
    print("="*70)
    
    # Configuration
    config = {
        'train_csv': 'datasets/brain_mri/splits/train.csv',
        'val_csv': 'datasets/brain_mri/splits/val.csv',
        'test_csv': 'datasets/brain_mri/splits/test.csv',
        'num_classes': 2,  # Gliome vs Normal (mais ce dataset ne contient que des gliomes)
        'num_epochs': 5,   # 5 epochs pour test rapide
        'output_dir': 'training_outputs/test_brain_mri'
    }
    
    print(f"\n📊 Configuration:")
    print(f"   Train CSV: {config['train_csv']}")
    print(f"   Val CSV: {config['val_csv']}")
    print(f"   Classes: {config['num_classes']}")
    print(f"   Epochs: {config['num_epochs']}")
    print(f"   Output: {config['output_dir']}")
    
    # Vérifier que les fichiers existent
    print(f"\n🔍 Vérification des fichiers...")
    train_file = Path(config['train_csv'])
    val_file = Path(config['val_csv'])
    test_file = Path(config['test_csv'])
    
    if not train_file.exists():
        print(f"❌ ERREUR: Fichier train non trouvé: {train_file}")
        print(f"   Exécutez d'abord: python create_brain_mri_split.py")
        return False
    
    if not val_file.exists():
        print(f"❌ ERREUR: Fichier val non trouvé: {val_file}")
        return False
    
    print(f"✅ Train file: {train_file} (existe)")
    print(f"✅ Val file: {val_file} (existe)")
    
    # Compter les images
    import pandas as pd
    train_df = pd.read_csv(train_file)
    val_df = pd.read_csv(val_file)
    
    print(f"\n📈 Statistiques:")
    print(f"   Images training: {len(train_df)}")
    print(f"   Images validation: {len(val_df)}")
    print(f"   Total: {len(train_df) + len(val_df)}")
    
    # Vérifier CUDA
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n💻 Device:")
    if device == 'cuda':
        print(f"   ✅ CUDA disponible: {torch.cuda.get_device_name(0)}")
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print(f"   ⚠️  CPU mode (plus lent)")
    
    # Créer le modèle
    print(f"\n🧠 Création du modèle...")
    try:
        model = create_default_model(num_classes=config['num_classes'])
        num_params = sum(p.numel() for p in model.parameters())
        print(f"   ✅ Modèle créé: EfficientNet-B0")
        print(f"   Paramètres: {num_params:,}")
    except Exception as e:
        print(f"   ❌ Erreur création modèle: {e}")
        return False
    
    # Créer le pipeline de training
    print(f"\n🚀 Initialisation du pipeline...")
    try:
        pipeline = TrainingPipeline(
            model=model,
            train_csv=config['train_csv'],
            val_csv=config['val_csv'],
            output_dir=config['output_dir'],
            device=device
        )
        print(f"   ✅ Pipeline initialisé")
        print(f"   Batch size: 32")
        print(f"   Optimizer: AdamW (lr=1e-4)")
        print(f"   Scheduler: CosineAnnealingLR")
    except Exception as e:
        print(f"   ❌ Erreur pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Lancer l'entraînement
    print(f"\n" + "="*70)
    print(f"🎯 DÉMARRAGE DE L'ENTRAÎNEMENT")
    print(f"="*70)
    print(f"\n⏱️  Temps estimé:")
    if device == 'cuda':
        print(f"   - Avec GPU: ~5-10 minutes ({config['num_epochs']} epochs)")
    else:
        print(f"   - Avec CPU: ~30-45 minutes ({config['num_epochs']} epochs)")
    print(f"\n💡 Le training va commencer. Vous verrez:")
    print(f"   - Progress bar par epoch")
    print(f"   - Loss et accuracy après chaque epoch")
    print(f"   - Sauvegarde du meilleur modèle")
    print(f"\n" + "-"*70)
    
    start_time = datetime.now()
    
    try:
        # Entraîner
        pipeline.train(
            num_epochs=config['num_epochs'],
            early_stopping_patience=3  # Stop si pas d'amélioration après 3 epochs
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n" + "="*70)
        print(f"✅ ENTRAÎNEMENT TERMINÉ!")
        print(f"="*70)
        print(f"\n⏱️  Durée: {duration/60:.1f} minutes ({duration:.0f} secondes)")
        print(f"📊 Epochs: {config['num_epochs']}")
        print(f"💾 Modèles sauvegardés dans: {pipeline.run_dir}")
        
        # Afficher le résumé
        history = pipeline.history
        print(f"\n📈 Résultats finaux:")
        print(f"   Train Loss: {history['train_loss'][-1]:.4f}")
        print(f"   Val Loss: {history['val_loss'][-1]:.4f}")
        print(f"   Train Acc: {history['train_acc'][-1]:.2f}%")
        print(f"   Val Acc: {history['val_acc'][-1]:.2f}%")
        
        # Trouver la meilleure epoch
        best_epoch = history['val_loss'].index(min(history['val_loss'])) + 1
        best_val_loss = min(history['val_loss'])
        best_val_acc = history['val_acc'][best_epoch - 1]
        
        print(f"\n🏆 Meilleure epoch: {best_epoch}")
        print(f"   Val Loss: {best_val_loss:.4f}")
        print(f"   Val Acc: {best_val_acc:.2f}%")
        
        # Fichiers générés
        print(f"\n📁 Fichiers générés:")
        print(f"   ✅ best_model.pth - Meilleur modèle")
        print(f"   ✅ final_model.pth - Modèle final")
        print(f"   ✅ training_curves.png - Courbes d'apprentissage")
        print(f"   ✅ training_history.json - Historique complet")
        
        # Analyse des résultats
        print(f"\n🔍 Analyse:")
        
        if best_val_acc > 70:
            print(f"   ✅ EXCELLENT - Accuracy > 70%")
            print(f"      Le modèle apprend correctement!")
        elif best_val_acc > 50:
            print(f"   ⚠️  MOYEN - Accuracy 50-70%")
            print(f"      Le modèle apprend mais peut être amélioré")
        else:
            print(f"   ❌ FAIBLE - Accuracy < 50%")
            print(f"      Le modèle n'apprend pas bien (normal pour un test rapide)")
        
        # Vérifier overfitting
        train_acc = history['train_acc'][-1]
        val_acc = history['val_acc'][-1]
        gap = train_acc - val_acc
        
        if gap < 5:
            print(f"   ✅ Pas d'overfitting (gap: {gap:.1f}%)")
        elif gap < 15:
            print(f"   ⚠️  Léger overfitting possible (gap: {gap:.1f}%)")
        else:
            print(f"   ⚠️  Overfitting détecté (gap: {gap:.1f}%)")
            print(f"      Train Acc: {train_acc:.1f}% | Val Acc: {val_acc:.1f}%")
        
        print(f"\n" + "="*70)
        print(f"🎉 TEST RÉUSSI - PIPELINE FONCTIONNEL!")
        print(f"="*70)
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Training interrompu par l'utilisateur")
        print(f"   Progression sauvegardée dans: {pipeline.run_dir}")
        return False
        
    except Exception as e:
        print(f"\n❌ ERREUR pendant l'entraînement:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Point d'entrée principal"""
    
    print("\n" + "="*70)
    print("IRMSIA - TEST DE TRAINING WORKFLOW")
    print("="*70)
    print(f"\n📚 Ce script va:")
    print(f"   1. Charger le dataset Brain MRI")
    print(f"   2. Créer un modèle Deep Learning (EfficientNet-B0)")
    print(f"   3. Entraîner pendant 5 epochs")
    print(f"   4. Sauvegarder les résultats")
    print(f"   5. Afficher un rapport complet")
    
    input(f"\n⏸️  Appuyez sur Enter pour continuer...")
    
    success = test_training_workflow()
    
    if success:
        print(f"\n✅ Le pipeline de training est opérationnel!")
        print(f"\n📖 Prochaines étapes:")
        print(f"   1. Voir les courbes: training_outputs/test_brain_mri/run_*/training_curves.png")
        print(f"   2. Lancer un training complet: 50 epochs au lieu de 5")
        print(f"   3. Tester avec d'autres datasets (COVID-19, etc.)")
        print(f"   4. Intégrer avec le serveur gRPC")
    else:
        print(f"\n⚠️  Le test a échoué. Vérifiez les erreurs ci-dessus.")
        print(f"\n💡 Solutions possibles:")
        print(f"   - Vérifier que les CSV existent: datasets/brain_mri/splits/")
        print(f"   - Réduire le batch_size si erreur de mémoire")
        print(f"   - Installer les dépendances: pip install -r requirements.txt")
    
    print(f"\n" + "="*70)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

