# 🔐 Identifiants de Connexion - Backend IRMSIA

## Utilisateurs par Défaut

Le backend contient deux utilisateurs pré-configurés :

### 👨‍💼 Administrateur
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: admin@irmsia.com
- **Rôle**: admin
- **Accès**: Accès complet à toutes les fonctionnalités

### 👨‍⚕️ Radiologiste
- **Username**: `radiologist`
- **Password**: `radio123`
- **Email**: radiologist@irmsia.com
- **Rôle**: radiologist
- **Accès**: Accès aux fonctionnalités de radiologie

## 🔒 Sécurité

⚠️ **IMPORTANT**: Ces identifiants sont pour le développement uniquement.

En production, vous devez :
1. Changer tous les mots de passe
2. Utiliser une vraie base de données
3. Implémenter une politique de mots de passe forte
4. Activer l'authentification à deux facteurs (2FA)

## 📝 Création de Nouveaux Utilisateurs

Vous pouvez créer de nouveaux utilisateurs via l'endpoint `/api/v1/auth/register` :

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nouvel_utilisateur",
    "email": "user@example.com",
    "password": "mot_de_passe_securise",
    "full_name": "Nom Complet",
    "role": "radiologist"
  }'
```

## 🚀 Connexion via le Frontend

1. Ouvrir http://localhost:3000/login (ou votre URL frontend)
2. Entrer l'username et le password
3. Cliquer sur "Se connecter"

## 🔍 Vérification

Pour vérifier que vous êtes connecté, vous pouvez appeler :

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer VOTRE_TOKEN_JWT"
```

