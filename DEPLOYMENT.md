# 🚀 Guide de Déploiement GitHub - IRMSIA

Ce guide vous explique comment déployer le projet IRMSIA sur GitHub.

## 📋 Prérequis

1. **Git installé** sur votre machine
2. **Compte GitHub** créé
3. **Accès en ligne de commande** (PowerShell sur Windows)

## 🔒 Sécurité - Fichiers à NE PAS commiter

Avant de déployer, assurez-vous que ces fichiers sont **exclus** du dépôt :

- ✅ `.env` (tous les fichiers .env)
- ✅ `*.db` (bases de données SQLite)
- ✅ `backend/storage/` (données médicales sensibles)
- ✅ `venv/` et `node_modules/` (dépendances)
- ✅ Fichiers de logs et crash
- ✅ Clés API et secrets

Ces fichiers sont déjà dans `.gitignore`, mais vérifiez avant de pousser !

## 🎯 Méthode 1 : Script Automatique (Recommandé)

### Étape 1 : Exécuter le script de déploiement

```powershell
# Depuis la racine du projet
.\scripts\deploy-github.ps1
```

Le script va :
1. ✅ Vérifier les fichiers sensibles
2. ✅ Afficher les fichiers à commiter
3. ✅ Créer un commit
4. ✅ Vous guider pour configurer le remote GitHub
5. ✅ Pousser le code

### Étape 2 : Suivre les instructions du script

Le script vous demandera :
- Confirmation pour ajouter les fichiers
- Message de commit (ou utilise le message par défaut)
- Configuration du remote GitHub si nécessaire
- Confirmation pour pousser

## 🎯 Méthode 2 : Déploiement Manuel

### Étape 1 : Vérifier l'état Git

```powershell
git status
```

### Étape 2 : Vérifier que les fichiers sensibles sont ignorés

```powershell
# Vérifier que .env est ignoré
git check-ignore .env
git check-ignore backend/.env
git check-ignore backend/medical_audit.db
```

### Étape 3 : Ajouter les fichiers

```powershell
# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Vérifier ce qui sera committé
git status
```

### Étape 4 : Créer un commit

```powershell
git commit -m "Initial commit: IRMSIA Medical AI System"
```

### Étape 5 : Créer le dépôt sur GitHub

1. Allez sur https://github.com/new
2. Nommez votre dépôt (ex: `irmsia`)
3. **Ne cochez PAS** "Initialize with README"
4. Cliquez sur "Create repository"

### Étape 6 : Connecter le dépôt local à GitHub

```powershell
# Ajouter le remote (remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub)
git remote add origin https://github.com/VOTRE_USERNAME/irmsia.git

# Renommer la branche en main (si nécessaire)
git branch -M main

# Vérifier le remote
git remote -v
```

### Étape 7 : Pousser le code

```powershell
# Pousser vers GitHub
git push -u origin main
```

Si vous êtes invité à vous authentifier :
- **Token GitHub** (recommandé) : Créez un Personal Access Token sur https://github.com/settings/tokens
- Ou utilisez **GitHub CLI** : `gh auth login`

## 🔐 Authentification GitHub

### Option 1 : Personal Access Token (Recommandé)

1. Allez sur https://github.com/settings/tokens
2. Cliquez sur "Generate new token (classic)"
3. Donnez un nom (ex: "IRMSIA Deployment")
4. Sélectionnez les scopes : `repo` (accès complet aux dépôts)
5. Copiez le token
6. Utilisez-le comme mot de passe lors du `git push`

### Option 2 : GitHub CLI

```powershell
# Installer GitHub CLI (si pas déjà installé)
# winget install GitHub.cli

# Se connecter
gh auth login

# Pousser
git push -u origin main
```

### Option 3 : SSH (Avancé)

```powershell
# Générer une clé SSH (si vous n'en avez pas)
ssh-keygen -t ed25519 -C "votre_email@example.com"

# Ajouter la clé à GitHub
# Copiez le contenu de ~/.ssh/id_ed25519.pub
# Allez sur https://github.com/settings/keys et ajoutez la clé

# Utiliser SSH pour le remote
git remote set-url origin git@github.com:VOTRE_USERNAME/irmsia.git
```

## ✅ Vérification Post-Déploiement

Après le déploiement, vérifiez :

1. **Dépôt GitHub** : https://github.com/VOTRE_USERNAME/irmsia
2. **Fichiers présents** : README.md, backend/, frontend-next/, etc.
3. **Fichiers absents** : .env, *.db, node_modules/, venv/
4. **README visible** : Le README.md doit s'afficher correctement

## 🔄 Mises à jour Futures

Pour mettre à jour le dépôt après des modifications :

```powershell
# Ajouter les modifications
git add .

# Créer un commit
git commit -m "Description des modifications"

# Pousser
git push
```

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

## 📚 Ressources

- [Documentation GitHub](https://docs.github.com/)
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [GitHub CLI](https://cli.github.com/)

## 🆘 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs d'erreur
2. Consultez la documentation GitHub
3. Vérifiez que tous les prérequis sont installés

---

**Bon déploiement ! 🚀**

