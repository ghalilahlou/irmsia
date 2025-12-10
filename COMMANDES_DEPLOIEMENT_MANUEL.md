# 📋 Commandes Manuelles de Déploiement GitHub - IRMSIA

Ce document contient toutes les commandes à exécuter **manuellement** pour déployer votre projet IRMSIA sur GitHub.

## 🔒 Étape 0 : Vérification de la Sécurité (IMPORTANT)

Avant de commiter, vérifiez que les fichiers sensibles sont bien ignorés :

```powershell
# Vérifier l'état Git
git status

# Vérifier que les fichiers sensibles sont ignorés
git check-ignore .env
git check-ignore backend/.env
git check-ignore frontend-next/.env
git check-ignore backend/medical_audit.db
git check-ignore medical_audit.db
```

Si ces commandes ne retournent rien, les fichiers ne sont pas ignorés. Vérifiez votre `.gitignore` !

---

## 📊 Étape 1 : Vérifier l'état du dépôt Git

```powershell
# Vérifier l'état actuel
git status
```

---

## ➕ Étape 2 : Ajouter les fichiers au staging

```powershell
# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Vérifier ce qui sera committé
git status
```

**⚠️ Vérifiez attentivement** que les fichiers suivants NE SONT PAS dans la liste :
- `.env` (tous les fichiers .env)
- `*.db` (bases de données)
- `venv/` et `node_modules/`
- `backend/storage/` (données sensibles)

---

## 💾 Étape 3 : Créer un commit

```powershell
# Créer un commit avec un message descriptif
git commit -m "Initial commit: IRMSIA Medical AI System"
```

Ou avec un message personnalisé :
```powershell
git commit -m "Votre message de commit personnalisé"
```

---

## 🌐 Étape 4 : Créer le dépôt sur GitHub (via navigateur)

1. Allez sur **https://github.com/new**
2. Nommez votre dépôt (ex: `irmsia`)
3. **⚠️ Ne cochez PAS** "Initialize with README"
4. Cliquez sur **"Create repository"**

---

## 🔗 Étape 5 : Connecter le dépôt local à GitHub

```powershell
# Ajouter le remote (remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub)
git remote add origin https://github.com/VOTRE_USERNAME/irmsia.git

# Si le remote existe déjà, supprimez-le d'abord :
# git remote remove origin
# git remote add origin https://github.com/VOTRE_USERNAME/irmsia.git

# Renommer la branche en main (si nécessaire)
git branch -M main

# Vérifier le remote
git remote -v
```

---

## 🚀 Étape 6 : Pousser le code vers GitHub

```powershell
# Pousser vers GitHub
git push -u origin main
```

---

## 🔐 Authentification GitHub

Si vous êtes invité à vous authentifier, vous avez 3 options :

### Option 1 : Personal Access Token (Recommandé)

1. Allez sur **https://github.com/settings/tokens**
2. Cliquez sur **"Generate new token (classic)"**
3. Donnez un nom (ex: "IRMSIA Deployment")
4. Sélectionnez le scope : **`repo`** (accès complet aux dépôts)
5. Cliquez sur **"Generate token"**
6. **Copiez le token** (vous ne pourrez plus le voir après)
7. Lors du `git push`, utilisez :
   - **Username** : Votre nom d'utilisateur GitHub
   - **Password** : Le token que vous venez de créer

### Option 2 : GitHub CLI

```powershell
# Installer GitHub CLI (si pas déjà installé)
winget install GitHub.cli

# Se connecter
gh auth login

# Pousser
git push -u origin main
```

### Option 3 : SSH (Avancé)

```powershell
# Générer une clé SSH (si vous n'en avez pas)
ssh-keygen -t ed25519 -C "votre_email@example.com"

# Afficher la clé publique
cat ~/.ssh/id_ed25519.pub
# Ou sur Windows PowerShell :
Get-Content ~/.ssh/id_ed25519.pub

# Copiez le contenu et ajoutez-le sur https://github.com/settings/keys

# Utiliser SSH pour le remote
git remote set-url origin git@github.com:VOTRE_USERNAME/irmsia.git

# Pousser
git push -u origin main
```

---

## ✅ Étape 7 : Vérification Post-Déploiement

Vérifiez que tout s'est bien passé :

1. **Visitez votre dépôt** : https://github.com/VOTRE_USERNAME/irmsia
2. **Vérifiez les fichiers présents** : README.md, backend/, frontend-next/, etc.
3. **Vérifiez les fichiers absents** : .env, *.db, node_modules/, venv/
4. **Vérifiez le README** : Le README.md doit s'afficher correctement

---

## 🔄 Mises à jour Futures

Pour mettre à jour le dépôt après des modifications :

```powershell
# Voir les modifications
git status

# Ajouter les modifications
git add .

# Créer un commit
git commit -m "Description des modifications"

# Pousser
git push
```

---

## 🐛 Dépannage

### Erreur : "remote origin already exists"

```powershell
# Vérifier le remote actuel
git remote -v

# Supprimer et recréer
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/irmsia.git
```

### Erreur : "Authentication failed"

- Vérifiez votre token GitHub
- Ou utilisez GitHub CLI : `gh auth login`
- Ou configurez SSH

### Erreur : "Permission denied"

- Vérifiez que vous avez les droits sur le dépôt
- Vérifiez que le nom d'utilisateur/repo est correct

### Fichiers sensibles committés par erreur

```powershell
# Retirer un fichier du cache Git (mais le garder localement)
git rm --cached backend/.env

# Créer un commit
git commit -m "Remove sensitive file"

# Pousser
git push
```

⚠️ **Important** : Si vous avez déjà poussé des fichiers sensibles, changez immédiatement vos clés/secréts !

---

## 📝 Résumé des Commandes Essentielles

```powershell
# 1. Vérifier l'état
git status

# 2. Ajouter les fichiers
git add .

# 3. Créer un commit
git commit -m "Initial commit: IRMSIA Medical AI System"

# 4. Ajouter le remote (une seule fois)
git remote add origin https://github.com/VOTRE_USERNAME/irmsia.git

# 5. Renommer la branche (si nécessaire)
git branch -M main

# 6. Pousser vers GitHub
git push -u origin main
```

---

**Bon déploiement ! 🚀**

