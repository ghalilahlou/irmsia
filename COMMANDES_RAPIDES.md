# ⚡ Commandes Rapides

## 🚀 Démarrer l'application

### Depuis la racine du projet (C:\Users\ghali\irmsia)

```powershell
# Option 1 : Script automatique
.\scripts\start.ps1

# Option 2 : Commande directe (RECOMMANDÉ)
python -m backend.main

# Option 3 : Avec uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ⚠️ Si vous êtes dans backend/

```powershell
# Revenir à la racine
cd ..

# Puis lancer
python -m backend.main
```

---

## 🔍 Vérifier votre position

```powershell
# Voir le répertoire actuel
pwd

# Vous devez être dans : C:\Users\ghali\irmsia
# PAS dans : C:\Users\ghali\irmsia\backend
```

---

## ✅ Vérification après démarrage

- Documentation API : http://localhost:8000/docs
- Health Check : http://localhost:8000/health

---

**IMPORTANT : Toujours lancer depuis la racine !** 🎯
