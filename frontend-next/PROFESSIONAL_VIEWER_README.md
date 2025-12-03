# 🏥 Professional DICOM Viewer - Documentation Complète

## Vue d'ensemble

Viewer DICOM professionnel style RadiAnt construit avec Next.js 14, Cornerstone.js, et TailwindCSS.

---

## ✨ Fonctionnalités Implémentées

### 🎯 Visualisation DICOM
- ✅ Support multi-series et multi-instances
- ✅ Chargement d'études complètes (plusieurs fichiers)
- ✅ Navigation frame par frame
- ✅ Support codecs compressés (JPEG2000, JPEG, RLE)
- ✅ Web Workers pour décodage rapide

### 🛠️ Outils de Navigation
- ✅ **Zoom** (Z) - Agrandissement/réduction
- ✅ **Pan** (P) - Déplacement de l'image
- ✅ **Window/Level** (W) - Ajustement contraste/luminosité
- ✅ **Scroll** (S) - Navigation dans le stack d'images

### 📏 Outils de Mesure
- ✅ **Length** (L) - Mesure de distance
- ✅ **Angle** (A) - Mesure d'angle
- ✅ **Rectangle ROI** (R) - Région d'intérêt rectangulaire
- ✅ **Ellipse ROI** (E) - Région d'intérêt elliptique
- ✅ **Probe** (B) - Valeur pixel

### 🔄 Transformations
- ✅ **Invert** (I) - Inversion de couleurs
- ✅ **Flip Horizontal** (H) - Miroir horizontal
- ✅ **Flip Vertical** (V) - Miroir vertical
- ✅ **Rotate** (Ctrl+R) - Rotation 90°
- ✅ **Fit to Window** (F) - Ajustement à la fenêtre
- ✅ **Reset** (Esc) - Réinitialisation

### 📊 Window/Level Presets
Presets cliniques par modalité:

**CT:**
- Abdomen (350/40)
- Bone (2000/300)
- Brain (80/40)
- Liver (150/30)
- Lung (1500/-600)
- Mediastinum (350/50)
- Subdural (200/75)

**MR:**
- Default (256/128)
- Brain (200/100)
- Spine (250/125)

**CR/DX:**
- Default (2048/1024)
- Chest (1500/500)

### 📐 Layouts Multi-View
- ✅ **1×1** - Vue unique
- ✅ **1×2** - Deux viewports côte à côte
- ✅ **2×2** - Quatre viewports en grille

### 🎨 Overlay DICOM
Affichage dans les 4 coins:
- **Haut Gauche:** Patient, Study, Date, Modality
- **Haut Droit:** Series Number, Series Description, Image Index
- **Bas Gauche:** Pixel Spacing, Slice Thickness, Location
- **Bas Droit:** Window/Level, Zoom, Dimensions

### ⌨️ Raccourcis Clavier
| Touche | Action |
|--------|--------|
| Z | Zoom |
| P | Pan |
| W | Window/Level |
| S | Scroll |
| L | Length Tool |
| A | Angle Tool |
| R | Rectangle ROI |
| E | Ellipse ROI |
| B | Probe |
| I | Invert |
| H | Flip Horizontal |
| V | Flip Vertical |
| F | Fit to Window |
| O | Toggle Overlay |
| Esc | Reset |
| Ctrl+R | Rotate 90° |
| Ctrl+S | Export PNG |

### 📤 Export
- ✅ Export PNG du viewport actif
- ✅ Qualité haute résolution
- ✅ Téléchargement automatique

---

## 📁 Architecture du Code

```
frontend-next/
├── app/
│   ├── viewer/                      # Viewer simple (existant)
│   │   ├── page.tsx
│   │   ├── dicomViewer.tsx
│   │   └── metadataPanel.tsx
│   │
│   └── professional-viewer/          # Viewer professionnel (nouveau)
│       └── page.tsx                  # Page principale du viewer pro
│
├── lib/
│   ├── cornerstone.ts               # Init Cornerstone + codecs
│   ├── dicomLoader.ts               # Loader simple (legacy)
│   │
│   └── dicom/                       # Architecture DICOM (nouveau)
│       ├── types.ts                 # Types TypeScript
│       ├── presets.ts               # W/L Presets
│       ├── studyLoader.ts           # Loader multi-series
│       └── viewportTools.ts         # Utilitaires viewport
│
├── components/
│   ├── UploadBox.tsx                # Upload drag & drop
│   ├── Toolbar.tsx                  # Toolbar simple (legacy)
│   │
│   └── dicom/                       # Composants DICOM (nouveau)
│       ├── ProfessionalViewport.tsx # Viewport avec overlay
│       ├── ProfessionalToolbar.tsx  # Toolbar complète
│       ├── DicomOverlay.tsx         # Overlay 4 coins
│       └── LayoutSelector.tsx       # Sélecteur layout
│
└── public/
    ├── cornerstoneWADOImageLoader.bundle.min.js
    └── codecs/                      # Web Workers codecs
```

---

## 🔧 Composants Principaux

### 1. **ProfessionalViewport.tsx**

Composant viewport avec toutes les fonctionnalités:

```typescript
<ProfessionalViewport
  ref={viewportRef}
  imageIds={imageIds}
  currentIndex={0}
  metadata={metadata}
  activeTool="pan"
  showOverlay={true}
  onIndexChange={(index) => console.log(index)}
  onError={(message) => console.error(message)}
/>
```

**Methods via ref:**
- `nextImage()` - Image suivante
- `previousImage()` - Image précédente
- `setImageIndex(index)` - Aller à l'index
- `applyPreset(preset)` - Appliquer preset W/L
- `invert()` - Inverser
- `flipHorizontal()` - Miroir H
- `flipVertical()` - Miroir V
- `rotate(degrees)` - Rotation
- `reset()` - Reset
- `fitToWindow()` - Fit
- `exportPng()` - Export PNG
- `getViewportStats()` - Stats viewport

### 2. **ProfessionalToolbar.tsx**

Toolbar complète avec tous les outils:

```typescript
<ProfessionalToolbar
  activeTool={activeTool}
  onSelectTool={setActiveTool}
  onInvert={() => viewportRef.current?.invert()}
  onFlipHorizontal={() => viewportRef.current?.flipHorizontal()}
  onFlipVertical={() => viewportRef.current?.flipVertical()}
  onRotate={() => viewportRef.current?.rotate(90)}
  onReset={() => viewportRef.current?.reset()}
  onFit={() => viewportRef.current?.fitToWindow()}
  onExport={handleExport}
  onPresetSelect={handlePresetSelect}
  windowLevelPresets={presets}
  disabled={false}
  showOverlay={true}
  onToggleOverlay={() => setShowOverlay(!showOverlay)}
/>
```

### 3. **studyLoader.ts**

Chargement d'études complètes:

```typescript
import { loadDicomStudy } from '@/lib/dicom/studyLoader';

const study = await loadDicomStudy(files);
// Returns:
// {
//   studyInstanceUID: string,
//   studyDescription: string,
//   patientName: string,
//   series: [
//     {
//       seriesInstanceUID: string,
//       seriesNumber: number,
//       modality: string,
//       instances: [
//         { instanceNumber, imageId, sopInstanceUID }
//       ]
//     }
//   ]
// }
```

### 4. **DicomOverlay.tsx**

Overlay avec métadonnées DICOM:

```typescript
<DicomOverlay
  metadata={metadata}
  currentIndex={5}
  totalImages={100}
  windowWidth={400}
  windowCenter={40}
  zoom={1.5}
/>
```

---

## 🚀 Utilisation

### Démarrage

```bash
cd frontend-next
npm run dev
```

Accédez à: `http://localhost:3000/professional-viewer`

### Workflow Typique

1. **Upload DICOM:**
   - Drag & drop de fichiers DICOM
   - Ou cliquez pour sélectionner
   - Accepte plusieurs fichiers (étude complète)

2. **Navigation:**
   - Utilisez la molette pour défiler les images
   - Clic gauche + drag pour Pan
   - Clic droit + drag pour Window/Level

3. **Mesures:**
   - Sélectionnez un outil de mesure (Length, Angle, ROI)
   - Cliquez et déplacez pour dessiner
   - Les valeurs s'affichent automatiquement

4. **Ajustements:**
   - Utilisez les presets W/L pour les ajustements rapides
   - Transformez l'image (Flip, Rotate, Invert)
   - Reset pour revenir à l'état initial

5. **Multi-View:**
   - Changez de layout (1×1, 1×2, 2×2)
   - Chaque viewport est indépendant
   - Possibilité de synchronisation (à implémenter)

6. **Export:**
   - Ctrl+S ou bouton Export
   - PNG haute qualité du viewport actif

---

## 🎨 Personnalisation

### Ajouter un Preset W/L

Éditez `lib/dicom/presets.ts`:

```typescript
export const WINDOW_LEVEL_PRESETS = {
  CT: [
    // ... existing presets
    { name: 'Custom', windowWidth: 400, windowCenter: 50, modality: 'CT' },
  ],
};
```

### Ajouter un Outil

1. Enregistrez l'outil dans `ProfessionalViewport.tsx`:

```typescript
cornerstoneTools.addTool(cornerstoneTools.MyCustomTool);
```

2. Ajoutez-le à la toolbar dans `ProfessionalToolbar.tsx`:

```typescript
const measurementTools = [
  // ... existing tools
  { tool: 'myCustom', icon: MyIcon, label: 'Custom', shortcut: 'C' },
];
```

3. Gérez l'activation dans `ProfessionalViewport.tsx`:

```typescript
case 'myCustom':
  cornerstoneTools.setToolActive('MyCustom', { mouseButtonMask: 1 });
  break;
```

---

## 🐛 Dépannage

### Image noire / Canvas vide

1. Vérifiez les logs console
2. Vérifiez que les codecs sont activés (Web Workers)
3. Testez avec un DICOM non-compressé

### Outils ne fonctionnent pas

1. Vérifiez que l'image est chargée (`isReady`)
2. Vérifiez les logs d'erreur
3. Assurez-vous que Cornerstone Tools est initialisé

### Erreur "element not enabled"

L'élément n'est pas encore enabled. Ajoutez des guards:

```typescript
if (!elementRef.current || !isReady) return;
```

---

## 📊 Performance

### Optimisations Implémentées

- ✅ Web Workers pour décodage DICOM
- ✅ Lazy loading des composants (dynamic import)
- ✅ Cache des images (Cornerstone cache)
- ✅ Cleanup propre des viewports

### Recommandations

- **Mémoire:** Limiter le nombre d'images en cache
- **CPU:** Utiliser Web Workers (déjà activé)
- **Réseau:** Précharger les images adjacentes

---

## 🔜 Améliorations Futures

### À Implémenter

- [ ] **Synchronisation viewports** (scroll, W/L)
- [ ] **Série thumbnails** (navigation par miniatures)
- [ ] **3D rendering** (MPR, VR)
- [ ] **Cine mode** (lecture automatique)
- [ ] **Annotations** (texte, flèches)
- [ ] **DICOM SR** (Structured Reports)
- [ ] **Fusion d'images** (PET/CT)
- [ ] **Histogram** affichage graphique
- [ ] **Crosshair** synchronisé
- [ ] **Stack synchronization** (même position anatomique)

---

## 📝 Notes Techniques

### Cornerstone Configuration

- **useWebWorkers:** `true` (décodage rapide)
- **maxWebWorkers:** `6` (ou `hardwareConcurrency`)
- **initializeCodecsOnStartup:** `true` (JPEG2000, JPEG, RLE)

### Types DICOM Supportés

- **Uncompressed** (1.2.840.10008.1.2)
- **JPEG Baseline** (1.2.840.10008.1.2.4.50)
- **JPEG2000 Lossless** (1.2.840.10008.1.2.4.90)
- **JPEG2000** (1.2.840.10008.1.2.4.91)
- **RLE Lossless** (1.2.840.10008.1.2.5)

### Modalités Testées

- ✅ CT (Computed Tomography)
- ✅ MR (Magnetic Resonance)
- ✅ CR (Computed Radiography)
- ✅ DX (Digital Radiography)
- ✅ OT (Other)

---

## 🎓 Ressources

- [Cornerstone Docs](https://docs.cornerstonejs.org/)
- [DICOM Standard](https://www.dicomstandard.org/)
- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS](https://tailwindcss.com/)

---

**Version:** 1.0.0  
**Date:** 2025-11-20  
**Statut:** ✅ Production Ready

