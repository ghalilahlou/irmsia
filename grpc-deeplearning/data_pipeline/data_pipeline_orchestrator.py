"""
Data Pipeline Orchestrator - Orchestration complète du pipeline de données
Menu interactif pour télécharger, préparer et entraîner
"""

import sys
from pathlib import Path
import logging
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.tcia_collector import TCIACollector, print_recommended_collections as print_tcia
from collectors.kaggle_collector import KaggleCollector, print_recommended_datasets as print_kaggle
from collectors.nih_collector import NIHCollector, print_recommended_datasets as print_nih
from processors.dataset_manager import DatasetManager
from training.training_pipeline import TrainingPipeline, create_default_model

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DataPipelineOrchestrator:
    """
    Orchestrateur du pipeline de données
    Interface unifiée pour tous les composants
    """
    
    def __init__(self, base_dir: str = "datasets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize collectors
        self.tcia = TCIACollector(output_dir=str(self.base_dir / "tcia"))
        self.kaggle = KaggleCollector(output_dir=str(self.base_dir / "kaggle"))
        self.nih = NIHCollector(output_dir=str(self.base_dir / "nih"))
        
        # Initialize dataset manager
        self.manager = DatasetManager(base_dir=str(self.base_dir))
        
        logger.info("Data Pipeline Orchestrator initialized")
    
    def show_main_menu(self):
        """Afficher le menu principal"""
        while True:
            print("\n" + "="*70)
            print("IRMSIA DATA PIPELINE - MENU PRINCIPAL")
            print("="*70)
            print("\n📥 1. Télécharger des datasets")
            print("📊 2. Gérer les datasets")
            print("🧠 3. Entraîner un modèle")
            print("📚 4. Documentation & Datasets recommandés")
            print("❌ 5. Quitter")
            
            choice = input("\nVotre choix (1-5): ").strip()
            
            if choice == '1':
                self.download_menu()
            elif choice == '2':
                self.manage_menu()
            elif choice == '3':
                self.training_menu()
            elif choice == '4':
                self.documentation_menu()
            elif choice == '5':
                print("\n👋 Au revoir!")
                break
            else:
                print("❌ Choix invalide")
    
    def download_menu(self):
        """Menu de téléchargement"""
        while True:
            print("\n" + "="*70)
            print("TÉLÉCHARGEMENT DE DATASETS")
            print("="*70)
            print("\n1. TCIA (The Cancer Imaging Archive)")
            print("2. Kaggle Medical Imaging")
            print("3. NIH ChestX-ray14")
            print("4. Retour au menu principal")
            
            choice = input("\nSource de téléchargement (1-4): ").strip()
            
            if choice == '1':
                self.tcia_download()
            elif choice == '2':
                self.kaggle_download()
            elif choice == '3':
                self.nih_download()
            elif choice == '4':
                break
            else:
                print("❌ Choix invalide")
    
    def tcia_download(self):
        """Téléchargement depuis TCIA"""
        print("\n📥 TCIA Download")
        print("\nCollections recommandées:")
        print("   1. LIDC-IDRI (Nodules pulmonaires, 1010 patients, ~124GB)")
        print("   2. TCGA-GBM (Glioblastome cérébral, 262 patients, ~50GB)")
        print("   3. COVID-19-AR (COVID thoracique, 201 patients, ~15GB)")
        print("   4. Lister toutes les collections")
        print("   5. Télécharger une collection spécifique")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == '1':
            print("\n⚠️  Cette collection fait ~124GB. Confirmez-vous le téléchargement?")
            confirm = input("Nombre max de patients (Enter = tous): ").strip()
            if not confirm or confirm.lower() in ['tous', 'tout', 'all']:
                max_patients = None
            else:
                try:
                    max_patients = int(confirm)
                except ValueError:
                    print(f"⚠️  Valeur invalide '{confirm}'. Téléchargement de tous les patients.")
                    max_patients = None
            self.tcia.download_collection("LIDC-IDRI", max_patients=max_patients)
        
        elif choice == '2':
            max_patients = input("Nombre max de patients (Enter = tous): ").strip()
            # Gérer "tous", "tout", ou valeur vide comme None
            if not max_patients or max_patients.lower() in ['tous', 'tout', 'all']:
                max_patients = None
            else:
                try:
                    max_patients = int(max_patients)
                except ValueError:
                    print(f"⚠️  Valeur invalide '{max_patients}'. Téléchargement de tous les patients.")
                    max_patients = None
            self.tcia.download_collection("TCGA-GBM", max_patients=max_patients)
        
        elif choice == '3':
            max_patients = input("Nombre max de patients (Enter = tous): ").strip()
            if not max_patients or max_patients.lower() in ['tous', 'tout', 'all']:
                max_patients = None
            else:
                try:
                    max_patients = int(max_patients)
                except ValueError:
                    print(f"⚠️  Valeur invalide '{max_patients}'. Téléchargement de tous les patients.")
                    max_patients = None
            self.tcia.download_collection("COVID-19-AR", max_patients=max_patients)
        
        elif choice == '4':
            collections = self.tcia.list_available_collections()
        
        elif choice == '5':
            collection_name = input("Nom de la collection: ").strip()
            max_patients = input("Nombre max de patients (Enter = tous): ").strip()
            if not max_patients or max_patients.lower() in ['tous', 'tout', 'all']:
                max_patients = None
            else:
                try:
                    max_patients = int(max_patients)
                except ValueError:
                    print(f"⚠️  Valeur invalide '{max_patients}'. Téléchargement de tous les patients.")
                    max_patients = None
            self.tcia.download_collection(collection_name, max_patients=max_patients)
    
    def kaggle_download(self):
        """Téléchargement depuis Kaggle"""
        print("\n📥 Kaggle Download")
        print("\n⚠️  Assurez-vous que Kaggle CLI est installé et configuré:")
        print("   pip install kaggle")
        print("   Configurez votre API key: ~/.kaggle/kaggle.json")
        
        print("\nDatasets recommandés:")
        print("   1. Brain MRI Segmentation (mateuszbuda/lgg-mri-segmentation)")
        print("   2. Chest X-Ray Pneumonia (paultimothymooney/chest-xray-pneumonia)")
        print("   3. COVID-19 Radiography (tawsifurrahman/covid19-radiography-database)")
        print("   4. Rechercher un dataset")
        print("   5. Télécharger un dataset spécifique")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == '1':
            self.kaggle.download_dataset("mateuszbuda/lgg-mri-segmentation")
        elif choice == '2':
            self.kaggle.download_dataset("paultimothymooney/chest-xray-pneumonia")
        elif choice == '3':
            self.kaggle.download_dataset("tawsifurrahman/covid19-radiography-database")
        elif choice == '4':
            query = input("Recherche: ").strip()
            self.kaggle.search_datasets(query)
        elif choice == '5':
            dataset_ref = input("Référence du dataset (user/dataset-name): ").strip()
            self.kaggle.download_dataset(dataset_ref)
    
    def nih_download(self):
        """Téléchargement depuis NIH"""
        print("\n📥 NIH ChestX-ray14 Download")
        print("\n⚠️  Ce dataset fait ~42GB (112,120 images)")
        print("\nOptions:")
        print("   1. Télécharger les labels uniquement (CSV)")
        print("   2. Instructions pour téléchargement complet")
        print("   3. Parser les labels et créer un split")
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == '1':
            self.nih.download_labels()
        elif choice == '2':
            self.nih.download_images_subset()
        elif choice == '3':
            self.nih.create_training_split()
    
    def manage_menu(self):
        """Menu de gestion des datasets"""
        while True:
            print("\n" + "="*70)
            print("GESTION DES DATASETS")
            print("="*70)
            print("\n1. Scanner et indexer un répertoire")
            print("2. Créer un split train/val/test")
            print("3. Voir les statistiques d'un dataset")
            print("4. Fusionner plusieurs datasets")
            print("5. Exporter pour training")
            print("6. Voir le résumé de tous les datasets")
            print("7. Retour au menu principal")
            
            choice = input("\nVotre choix (1-7): ").strip()
            
            if choice == '1':
                directory = input("Répertoire à scanner: ").strip()
                dataset_name = input("Nom du dataset: ").strip()
                self.manager.scan_directory(directory, dataset_name)
            
            elif choice == '2':
                dataset_name = input("Nom du dataset: ").strip()
                self.manager.create_train_val_test_split(dataset_name)
            
            elif choice == '3':
                dataset_name = input("Nom du dataset: ").strip()
                self.manager.get_dataset_statistics(dataset_name)
            
            elif choice == '4':
                dataset_names = input("Noms des datasets (séparés par virgule): ").strip().split(',')
                dataset_names = [name.strip() for name in dataset_names]
                output_name = input("Nom du dataset fusionné: ").strip()
                self.manager.merge_datasets(dataset_names, output_name)
            
            elif choice == '5':
                dataset_name = input("Nom du dataset: ").strip()
                split = input("Split (train/val/test): ").strip()
                self.manager.export_for_training(dataset_name, split)
            
            elif choice == '6':
                self.manager.print_summary()
            
            elif choice == '7':
                break
            
            else:
                print("❌ Choix invalide")
    
    def training_menu(self):
        """Menu d'entraînement"""
        print("\n" + "="*70)
        print("ENTRAÎNEMENT D'UN MODÈLE")
        print("="*70)
        
        print("\nPour entraîner un modèle, vous devez avoir:")
        print("   1. Un dataset préparé avec split train/val/test")
        print("   2. Des fichiers CSV avec les chemins et labels")
        
        proceed = input("\nContinuer? (y/n): ").strip().lower()
        
        if proceed != 'y':
            return
        
        train_csv = input("Path vers train.csv: ").strip()
        val_csv = input("Path vers val.csv: ").strip()
        num_classes = input("Nombre de classes: ").strip()
        num_epochs = input("Nombre d'epochs (défaut: 50): ").strip()
        
        num_classes = int(num_classes)
        num_epochs = int(num_epochs) if num_epochs else 50
        
        print("\n🚀 Démarrage de l'entraînement...")
        
        # Créer le modèle
        model = create_default_model(num_classes=num_classes)
        
        # Créer le pipeline
        pipeline = TrainingPipeline(
            model=model,
            train_csv=train_csv,
            val_csv=val_csv,
            output_dir="training_outputs"
        )
        
        # Entraîner
        pipeline.train(num_epochs=num_epochs)
    
    def documentation_menu(self):
        """Menu de documentation"""
        while True:
            print("\n" + "="*70)
            print("DOCUMENTATION & DATASETS RECOMMANDÉS")
            print("="*70)
            print("\n1. Datasets TCIA recommandés")
            print("2. Datasets Kaggle recommandés")
            print("3. Datasets NIH recommandés")
            print("4. Guide de démarrage rapide")
            print("5. Retour au menu principal")
            
            choice = input("\nVotre choix (1-5): ").strip()
            
            if choice == '1':
                print_tcia()
            elif choice == '2':
                print_kaggle()
            elif choice == '3':
                print_nih()
            elif choice == '4':
                self.print_quick_start()
            elif choice == '5':
                break
            else:
                print("❌ Choix invalide")
    
    def print_quick_start(self):
        """Afficher le guide de démarrage rapide"""
        print("\n" + "="*70)
        print("GUIDE DE DÉMARRAGE RAPIDE")
        print("="*70)
        
        print("""
🚀 Workflow complet:

1️⃣ TÉLÉCHARGER UN DATASET
   Menu Principal → Télécharger des datasets
   Exemple: Kaggle Brain MRI Segmentation (1.5GB)

2️⃣ INDEXER LE DATASET
   Menu Principal → Gérer les datasets → Scanner et indexer
   - Répertoire: datasets/kaggle/mateuszbuda_lgg-mri-segmentation
   - Nom: brain_mri

3️⃣ CRÉER UN SPLIT
   Menu Principal → Gérer les datasets → Créer un split
   - Dataset: brain_mri
   - Génère: train.csv, val.csv, test.csv

4️⃣ ENTRAÎNER UN MODÈLE
   Menu Principal → Entraîner un modèle
   - Train CSV: datasets/brain_mri/splits/train.csv
   - Val CSV: datasets/brain_mri/splits/val.csv
   - Classes: 2 (tumeur / normal)
   - Epochs: 50

5️⃣ ÉVALUER LES RÉSULTATS
   - Modèles sauvegardés: training_outputs/run_YYYYMMDD_HHMMSS/
   - Courbes d'apprentissage: training_curves.png
   - Historique: training_history.json

📊 Datasets recommandés pour commencer:
   - Brain MRI Segmentation (Kaggle, 1.5GB) → Gliomes cérébraux
   - Chest X-Ray Pneumonia (Kaggle, 2.2GB) → Pneumonie
   - COVID-19 Radiography (Kaggle, 1.2GB) → COVID thoracique

💡 Conseil: Commencez par un petit dataset pour tester le pipeline!
        """)


def main():
    """Point d'entrée principal"""
    print("\n" + "="*70)
    print("IRMSIA DATA PIPELINE ORCHESTRATOR")
    print("Pipeline complet pour import, préparation et training de datasets DICOM")
    print("="*70)
    
    orchestrator = DataPipelineOrchestrator()
    orchestrator.show_main_menu()


if __name__ == "__main__":
    main()

