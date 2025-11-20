"""
Script pour créer des données de test IRM
Génère des images DICOM et NIfTI de test pour le développement
"""

import numpy as np
import nibabel as nib
from pathlib import Path
import os

def create_test_dicom():
    """Crée un fichier DICOM de test"""
    try:
        import pydicom
        from pydicom.dataset import FileDataset, FileMetaDataset
        
        # Créer une image de test (cerveau simulé)
        image_data = create_brain_phantom()
        
        # Créer les métadonnées DICOM
        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        file_meta.MediaStorageSOPInstanceUID = '1.2.3.4.5.6.7.8.9'
        file_meta.ImplementationClassUID = '1.2.3.4.5.6.7.8.9'
        
        ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)
        
        # Métadonnées DICOM
        ds.PatientName = "Test Patient"
        ds.PatientID = "TEST001"
        ds.Modality = "MR"
        ds.StudyDate = "20240101"
        ds.StudyTime = "120000"
        ds.StudyDescription = "Test IRM"
        ds.SeriesDescription = "Test Series"
        ds.ImageType = ['ORIGINAL', 'PRIMARY', 'AXIAL']
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelRepresentation = 0
        ds.HighBit = 15
        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.Columns = image_data.shape[1]
        ds.Rows = image_data.shape[0]
        ds.PixelData = image_data.tobytes()
        
        # Sauvegarder
        output_path = Path(__file__).parent / "test_brain.dcm"
        ds.save_as(str(output_path))
        print(f"✅ Fichier DICOM créé: {output_path}")
        
        return output_path
        
    except ImportError:
        print("❌ pydicom non disponible, impossible de créer le fichier DICOM")
        return None

def create_test_nifti():
    """Crée un fichier NIfTI de test"""
    try:
        # Créer une image de test (cerveau simulé)
        image_data = create_brain_phantom()
        
        # Créer l'objet NIfTI
        nii_img = nib.Nifti1Image(image_data, np.eye(4))
        
        # Sauvegarder
        output_path = Path(__file__).parent / "test_brain.nii.gz"
        nib.save(nii_img, str(output_path))
        print(f"✅ Fichier NIfTI créé: {output_path}")
        
        return output_path
        
    except ImportError:
        print("❌ nibabel non disponible, impossible de créer le fichier NIfTI")
        return None

def create_brain_phantom():
    """Crée un fantôme de cerveau simulé"""
    # Créer une image 256x256
    size = 256
    image = np.zeros((size, size), dtype=np.uint16)
    
    # Créer des structures cérébrales simulées
    center = size // 2
    
    # Crâne (cercle externe)
    y, x = np.ogrid[:size, :size]
    skull_mask = (x - center)**2 + (y - center)**2 <= (size//2 - 10)**2
    image[skull_mask] = 1000
    
    # Cerveau (cercle interne)
    brain_mask = (x - center)**2 + (y - center)**2 <= (size//2 - 30)**2
    image[brain_mask] = 800
    
    # Ventricules (petits cercles)
    ventricle1_mask = (x - (center - 20))**2 + (y - (center - 10))**2 <= 15**2
    ventricle2_mask = (x - (center + 20))**2 + (y - (center - 10))**2 <= 15**2
    image[ventricle1_mask] = 200
    image[ventricle2_mask] = 200
    
    # Substance grise (cercles plus petits)
    gray_matter1 = (x - (center - 40))**2 + (y - (center - 30))**2 <= 25**2
    gray_matter2 = (x - (center + 40))**2 + (y - (center - 30))**2 <= 25**2
    gray_matter3 = (x - center)**2 + (y - (center + 40))**2 <= 30**2
    image[gray_matter1] = 600
    image[gray_matter2] = 600
    image[gray_matter3] = 600
    
    # Ajouter du bruit pour plus de réalisme
    noise = np.random.normal(0, 20, image.shape).astype(np.int16)
    image = np.clip(image + noise, 0, 65535).astype(np.uint16)
    
    return image

def create_segmentation_test_data():
    """Crée des données de test pour la segmentation"""
    # Image originale
    original = create_brain_phantom()
    
    # Segmentation simulée (labels: 0=background, 1=cerveau, 2=ventricules, 3=tumeur)
    segmentation = np.zeros_like(original, dtype=np.uint8)
    
    size = original.shape[0]
    center = size // 2
    y, x = np.ogrid[:size, :size]
    
    # Cerveau (label 1)
    brain_mask = (x - center)**2 + (y - center)**2 <= (size//2 - 30)**2
    segmentation[brain_mask] = 1
    
    # Ventricules (label 2)
    ventricle1_mask = (x - (center - 20))**2 + (y - (center - 10))**2 <= 15**2
    ventricle2_mask = (x - (center + 20))**2 + (y - (center - 10))**2 <= 15**2
    segmentation[ventricle1_mask] = 2
    segmentation[ventricle2_mask] = 2
    
    # Tumeur simulée (label 3)
    tumor_mask = (x - (center + 30))**2 + (y - (center + 20))**2 <= 12**2
    segmentation[tumor_mask] = 3
    
    # Sauvegarder
    output_path = Path(__file__).parent / "test_segmentation.nii.gz"
    nii_img = nib.Nifti1Image(segmentation, np.eye(4))
    nib.save(nii_img, str(output_path))
    print(f"✅ Données de segmentation créées: {output_path}")
    
    return output_path

def main():
    """Fonction principale pour créer toutes les données de test"""
    print("🧠 Création des données de test IRMSIA")
    print("=" * 50)
    
    # Créer le répertoire data s'il n'existe pas
    data_dir = Path(__file__).parent
    data_dir.mkdir(exist_ok=True)
    
    # Créer les fichiers de test
    dicom_file = create_test_dicom()
    nifti_file = create_test_nifti()
    seg_file = create_segmentation_test_data()
    
    print("\n📁 Fichiers de test créés:")
    if dicom_file:
        print(f"  - DICOM: {dicom_file}")
    if nifti_file:
        print(f"  - NIfTI: {nifti_file}")
    if seg_file:
        print(f"  - Segmentation: {seg_file}")
    
    print("\n✅ Données de test prêtes pour le développement!")

if __name__ == "__main__":
    main() 