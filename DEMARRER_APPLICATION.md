# 🚀 Comment Démarrer l'Application

## ✅ Solution Simple

### Depuis la racine du projet (C:\Users\ghali\irmsia)

```powershell
# Méthode 1 : Script automatique
.\scripts\start.ps1

# Méthode 2 : Commande directe
python -m backend.main

# Méthode 3 : Avec uvicorn directement
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ⚠️ Ne PAS lancer depuis backend/

Si vous êtes dans `backend/`, revenez à la racine :

```powershell
cd ..
python -m backend.main
```

---

## 🔧 Pourquoi ce problème ?

Les imports utilisent `from backend.core.config import settings`. Python doit donc voir le dossier `backend/` comme un module, ce qui nécessite d'être à la racine du projet.

---

## ✅ Vérification

Une fois lancé, ouvrez :
- http://localhost:8000/docs
- http://localhost:8000/health

---

**Lancez depuis la racine : `python -m backend.main` 🎉**

