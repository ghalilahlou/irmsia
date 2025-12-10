# 🚀 Guide de Déploiement Force - Remplacement Complet du Dépôt GitHub

## ⚠️ ATTENTION

**Cette opération est DESTRUCTIVE et IRRÉVERSIBLE !**

Le script `force-deploy-github` va :
- ✅ Supprimer **TOUT** l'historique Git sur GitHub
- ✅ Remplacer par votre version locale actuelle
- ✅ Écraser toutes les branches et commits distants

**Utilisez cette méthode uniquement si :**
- Vous voulez complètement remplacer le dépôt GitHub
- Vous avez sauvegardé tout ce qui est important
- Vous êtes sûr de vouloir perdre l'historique distant

## 📋 Prérequis

1. **Git installé** et configuré
2. **Remote GitHub configuré** : `git remote -v` doit afficher votre dépôt
3. **Accès au dépôt** : Permissions en écriture sur GitHub
4. **Fichiers sensibles exclus** : Vérifiez que `.env`, `*.db`, etc. sont dans `.gitignore`

## 🚀 Utilisation

### Windows (PowerShell)

```powershell
# Depuis la racine du projet
.\scripts\force-deploy-github.ps1
```

Avec un message de commit personnalisé :
```powershell
.\scripts\force-deploy-github.ps1 -CommitMessage "Nouveau déploiement avec Docker"
```

Sans confirmation (pour scripts automatisés) :
```powershell
.\scripts\force-deploy-github.ps1 -SkipConfirmation
```

### Linux/Mac (Bash)

```bash
# Rendre le script exécutable (première fois)
chmod +x scripts/force-deploy-github.sh

# Exécuter
./scripts/force-deploy-github.sh
```

Avec un message de commit personnalisé :
```bash
./scripts/force-deploy-github.sh "Nouveau déploiement avec Docker"
```

## 📝 Étapes du Script

Le script effectue les opérations suivantes :

1. **Vérifications** :
   - Git installé
   - Dépôt Git valide
   - Remote configuré
   - Fichiers sensibles détectés

2. **Confirmation** :
   - Demande de confirmation avant de continuer
   - Avertissement sur la nature destructive

3. **Préparation** :
   - `git add -A` : Ajoute tous les fichiers (modifiés et nouveaux)
   - `git commit` : Crée un commit avec votre message

4. **Déploiement** :
   - `git push --force` : Force push pour remplacer complètement le dépôt distant

## 🔍 Vérification Avant Déploiement

### 1. Vérifier les fichiers à commiter

```powershell
git status
```

Assurez-vous que :
- ✅ Les nouveaux fichiers Docker sont inclus
- ✅ Les modifications sont correctes
- ❌ Aucun fichier sensible (`.env`, `*.db`) n'est inclus

### 2. Vérifier le remote

```powershell
git remote -v
```

Doit afficher :
```
origin  https://github.com/VOTRE_USERNAME/irmsia.git (fetch)
origin  https://github.com/VOTRE_USERNAME/irmsia.git (push)
```

### 3. Vérifier la branche

```powershell
git branch
```

Vous devez être sur `main` ou `master`.

## 🔐 Authentification GitHub

Le script nécessite une authentification GitHub. Options :

### Option 1 : Personal Access Token (Recommandé)

1. Créez un token sur : https://github.com/settings/tokens
2. Sélectionnez le scope `repo` (accès complet)
3. Utilisez le token comme mot de passe lors du push

### Option 2 : GitHub CLI

```powershell
gh auth login
```

### Option 3 : SSH

Configurez une clé SSH et utilisez l'URL SSH pour le remote :
```powershell
git remote set-url origin git@github.com:VOTRE_USERNAME/irmsia.git
```

## 📊 Après le Déploiement

### Vérifier sur GitHub

1. Allez sur votre dépôt : https://github.com/VOTRE_USERNAME/irmsia
2. Vérifiez que tous les fichiers sont présents
3. Vérifiez que l'historique a été remplacé (un seul commit)

### Vérifier localement

```powershell
git log --oneline
git remote show origin
```

## 🐛 Dépannage

### Erreur : "Permission denied"

**Solution** :
- Vérifiez vos permissions sur le dépôt GitHub
- Vérifiez votre authentification (token/SSH)

### Erreur : "Remote origin already exists"

**Solution** : Le remote est déjà configuré, c'est normal. Continuez.

### Erreur : "Nothing to commit"

**Solution** : Tous les fichiers sont déjà commités. Le script proposera de forcer le push quand même.

### Erreur : "Authentication failed"

**Solution** :
- Vérifiez votre token GitHub
- Ou utilisez GitHub CLI : `gh auth login`

### Fichiers sensibles détectés

**Solution** :
1. Vérifiez que les fichiers sont dans `.gitignore`
2. Si déjà commités, retirez-les :
   ```powershell
   git rm --cached fichier.env
   git commit -m "Remove sensitive file"
   ```

## 🔄 Alternative : Déploiement Normal (Sans Force)

Si vous ne voulez **PAS** supprimer l'historique, utilisez le script normal :

```powershell
.\scripts\deploy-github.ps1
```

Cela ajoutera vos changements à l'historique existant au lieu de le remplacer.

## 📚 Commandes Manuelles

Si vous préférez faire manuellement :

```powershell
# 1. Ajouter tous les fichiers
git add -A

# 2. Créer un commit
git commit -m "Complete repository replacement with new Docker deployment"

# 3. Force push
git push origin main --force
```

## ⚠️ Avertissements Importants

1. **Sauvegarde** : Assurez-vous d'avoir une sauvegarde de tout ce qui est important
2. **Collaboration** : Si d'autres personnes travaillent sur le dépôt, **coordonnez-vous** avant de faire un force push
3. **Branches** : Toutes les branches distantes seront remplacées
4. **Issues/PRs** : Les issues et pull requests ne seront pas affectées, mais l'historique des commits sera perdu

## 🆘 Support

En cas de problème :

1. Vérifiez les logs du script
2. Vérifiez votre authentification GitHub
3. Consultez la documentation GitHub : https://docs.github.com/

---

**Utilisez avec précaution ! ⚠️**

