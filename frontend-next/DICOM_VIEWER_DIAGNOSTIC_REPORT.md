# 🔍 RAPPORT DE DIAGNOSTIC - DICOM Viewer

## Date: 2025-11-20
## Issue: Canvas noir - image DICOM ne s'affiche pas

---

## ✅ COMPOSANTS INSTALLÉS

### Dépendances Cornerstone
- `cornerstone-core@2.6.1` ✅
- `cornerstone-tools@4.21.2` ✅
- `cornerstone-wado-image-loader@4.13.1` ✅
- `dicom-parser@1.8.21` ✅
- `cornerstone-math@0.1.10` ✅
- `hammerjs@2.0.8` ✅

---

## 📋 ARCHITECTURE ACTUELLE

```
/app/viewer/
  ├── page.tsx              → Orchestration (upload + toolbar + viewer + metadata)
  ├── dicomViewer.tsx       → Composant Cornerstone (canvas + outils)
  └── metadataPanel.tsx     → Affichage metadata (PHI masqué)

/lib/
  ├── cornerstone.ts        → Init Cornerstone + config workers
  └── dicomLoader.ts        → Parse DICOM + génère imageIds

/components/
  ├── UploadBox.tsx         → Drag & drop fichiers
  └── Toolbar.tsx           → Boutons contrôle (Zoom, Pan, W/L, etc.)

/api/convert/
  └── route.ts              → Export PNG (canvas → base64)
```

---

## 🐛 PROBLÈMES IDENTIFIÉS

### 1. **Web Workers CSP Bloqués** (RÉSOLU PARTIELLEMENT)
**Symptôme**: `Creating a worker from 'blob:...' violates CSP`  
**Cause**: `cornerstone-wado-image-loader` essaie de créer des workers pour décoder DICOM  
**Tentatives de fix**:
- ✅ Config `useWebWorkers: false` dans `lib/cornerstone.ts` (ligne 40)
- ✅ Config immédiate au top-level (ligne 10-18)
- ✅ Ajout `worker-src 'self' blob:` dans CSP (`next.config.js` ligne 60)

**État**: Workers autorisés maintenant, mais config `useWebWorkers: false` non respectée

---

### 2. **Canvas Noir - Image ne s'affiche pas**
**Symptôme**: Métadonnées chargées ✅, mais canvas reste noir ❌  
**Causes possibles**:

#### A) Problème de rendu Cornerstone
- `cornerstone.displayImage()` appelé mais ne rend rien
- Viewport Window/Level mal initialisé
- Canvas dimensions = 0 ou non attaché au DOM

#### B) Problème de décodage DICOM
- Image chargée mais pixel data corrompu/illisible
- Format pixel non supporté (compressed transfer syntax?)
- Worker décodage échoue silencieusement

#### C) Problème React/DOM
- `useLayoutEffect` timing : canvas pas prêt quand Cornerstone s'init
- React unmount/remount pendant le chargement
- `elementRef.current` null au moment du render

---

### 3. **Erreurs React DOM** (RÉSOLU)
**Symptôme**: `removeChild/insertBefore` errors  
**Fix appliqué**: 
- Ne plus appeler `cornerstone.disable()` dans le cleanup
- Flag `mounted` pour éviter state updates après unmount

---

## 🔬 DIAGNOSTIC ACTIVÉ

### Logs ajoutés dans le code

**`lib/dicomLoader.ts`:**
```typescript
console.log('[DICOM Loader] Loading X file(s)')
console.log('[DICOM Loader] Processing file:', file.name, size)
console.log('[DICOM Loader] File parsed:', {
  baseImageId, numberOfFrames, instanceNumber, modality,
  rows, columns, bitsAllocated, bitsStored, pixelRepresentation
})
console.log('[DICOM Loader] Loaded stack:', { totalFrames, firstImageId, metadata })
```

**`app/viewer/dicomViewer.tsx`:**
```typescript
console.log('[DICOM Viewer] Starting load for imageId:', ...)
console.log('[DICOM Viewer] Image loaded:', { width, height, windowWidth, windowCenter, ... })
console.log('[DICOM Viewer] Image displayed')
console.log('[DICOM Viewer] Initial viewport:', viewport)
console.log('[DICOM Viewer] Setting viewport:', newViewport)
console.log('[DICOM Viewer] Tools activated, ready!')
console.error('[DICOM Viewer] Load error:', error, stack)
```

---

## 📊 ÉTAPES DE TEST

### Test avec fichier spécifique
**Fichier**: `C:\Users\ghali\Downloads\Anonymized_20251120\series-00000\image-00000.dcm`

**Procédure**:
1. Ouvrir console navigateur (F12)
2. Charger http://localhost:3000/viewer
3. Upload le fichier DICOM
4. Observer les logs console dans cet ordre:

```
[DICOM Loader] Loading 1 file(s)
[DICOM Loader] Processing file: image-00000.dcm size: XXXXX bytes
[DICOM Loader] File parsed: { ... }
[DICOM Loader] Loaded stack: { totalFrames: 1, firstImageId: 'wadouri:...', ... }
[DICOM Viewer] Starting load for imageId: wadouri:...
[DICOM Viewer] Image loaded: { width: XXX, height: XXX, ... }
[DICOM Viewer] Image displayed
[DICOM Viewer] Initial viewport: { ... }
[DICOM Viewer] Setting viewport: { ... }
[DICOM Viewer] Tools activated, ready!
```

**Vérifications**:
- ✅ Tous les logs apparaissent sans erreur
- ✅ `image.width` et `image.height` > 0
- ✅ `viewport.voi.windowWidth` et `windowCenter` définis
- ❌ **Canvas reste noir** malgré tout

---

## 🎯 HYPOTHÈSES RESTANTES

### Hypothèse #1: Transfer Syntax non supporté
Si le DICOM est compressé (JPEG, JPEG2000, RLE), Cornerstone-core seul ne peut pas le décoder.  
**Solution**: Vérifier Transfer Syntax UID dans les logs, activer les codecs appropriés

### Hypothèse #2: Photometric Interpretation
Si l'image est `MONOCHROME1` (pixels inversés), elle peut paraître noire.  
**Solution**: Forcer `invert: true` dans viewport initial

### Hypothèse #3: Canvas rendering context
Le canvas existe mais le contexte WebGL/2D n'est pas initialisé correctement.  
**Solution**: Inspecter `enabledElement.canvas` dans le DOM

### Hypothèse #4: CSS masque le canvas
Le canvas est rendu mais masqué par du CSS (z-index, opacity, clip-path).  
**Solution**: Inspecter l'élément dans DevTools → Computed styles

---

## 🛠️ PROCHAINES ÉTAPES

1. **Relancer le serveur** avec les nouveaux logs
2. **Recharger le fichier DICOM** et copier TOUS les logs console
3. **Analyser les valeurs**:
   - `image.width` / `image.height`
   - `image.windowWidth` / `image.windowCenter`
   - `image.minPixelValue` / `maxPixelValue`
   - `image.color` (true/false)
   - `viewport.scale`, `viewport.translation`
4. **Inspecter le DOM**: 
   - Canvas existe ? Dimensions ?
   - `<canvas>` a un contexte de rendu ?
5. **Screenshot du canvas** via DevTools

---

## 📞 INFORMATIONS NÉCESSAIRES

Pour résoudre définitivement, il faut:
1. **Copie complète des logs console** après upload du fichier
2. **Screenshot de l'onglet "Elements"** (DevTools) montrant le `<canvas>`
3. **Propriétés calculées** du canvas (width, height, display, visibility)
4. **Transfer Syntax UID** du fichier DICOM (visible dans les metadata DICOM)

---

## 📝 RÉSUMÉ CONFIG ACTUELLE

### `lib/cornerstone.ts`
- Init immédiate : `useWebWorkers: false`, `decodeConfig` défini
- Externe: cornerstone, dicomParser, Hammer liés

### `next.config.js`
- CSP: `worker-src 'self' blob:` autorisé
- Images: blob, data URLs autorisés

### `app/viewer/dicomViewer.tsx`
- `useLayoutEffect` pour init Cornerstone
- Viewport forcé avec W/L par défaut (256/128)
- Logs détaillés activés

### `lib/dicomLoader.ts`
- Import dynamique de Cornerstone (évite SSR)
- Parse avec dicom-parser
- Logs détaillés activés

---

**Statut**: 🟡 EN ATTENTE DES LOGS CONSOLE POUR DIAGNOSTIC FINAL

