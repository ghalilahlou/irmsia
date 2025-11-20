# 🔧 Troubleshooting

## Erreur Content Security Policy (CSP)

### Symptôme
```
Connecting to 'http://localhost:8000/api/v1/auth/login' violates the following Content Security Policy directive: "default-src 'self'"
Network Error
AxiosError
```

### Cause
La Content Security Policy (CSP) dans `next.config.js` bloque les connexions vers le backend car la directive `connect-src` n'autorise pas `localhost:8000`.

### Solution
✅ **Corrigé dans `next.config.js`** : La directive `connect-src` a été ajoutée pour autoriser les connexions vers le backend.

**Important** : Après modification de `next.config.js`, vous devez **redémarrer le serveur Next.js** :
```bash
# Arrêtez le serveur (Ctrl+C)
# Puis redémarrez
cd frontend-next
npm run dev
```

## Erreur d'hydratation React

### Symptôme
```
A tree hydrated but some attributes of the server rendered HTML didn't match the client properties.
```

### Cause
Cette erreur peut être causée par :
1. **Extensions de navigateur** (ex: Google Translate) qui modifient le HTML
2. Utilisation de `Date.now()` ou `Math.random()` dans le rendu initial
3. Formatage de dates avec des locales différentes
4. Branches conditionnelles serveur/client

### Solution
Le problème a été corrigé en ajoutant `suppressHydrationWarning` sur les éléments `<html>` et `<body>` dans `app/layout.tsx`.

Si l'erreur persiste :

1. **Désactiver les extensions de navigateur** temporairement
2. **Vérifier les composants** qui utilisent des valeurs dynamiques
3. **S'assurer** que tous les composants avec dates/random sont marqués `'use client'`

## Erreurs de connexion API

### Symptôme
```
Network Error
Failed to fetch
CORS error
```

### Solutions
1. **Vérifier que le backend est lancé** sur `http://localhost:8000`
   ```bash
   # Testez avec curl ou navigateur
   curl http://localhost:8000/health
   ```

2. **Vérifier `NEXT_PUBLIC_API_URL`** dans `.env.local`
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Vérifier les CORS dans le backend FastAPI**
   - Le backend doit autoriser `http://localhost:3000` dans `ALLOWED_HOSTS`

4. **Vérifier la console du navigateur** pour plus de détails

5. **Redémarrer le serveur Next.js** après modification de `next.config.js`

## Problèmes d'authentification

### Symptôme
```
401 Unauthorized
Token expired
Redirect loop
```

### Solutions
1. Vérifier que le cookie `irmsia_token` est bien défini
2. Vérifier la validité du token JWT
3. Se déconnecter et se reconnecter
4. Vérifier les endpoints d'authentification dans le backend

## Erreurs de build

### Symptôme
```
TypeScript errors
Module not found
Build failed
```

### Solutions
1. Supprimer `.next` et rebuilder : 
   ```bash
   rm -rf .next
   npm run build
   ```

2. Réinstaller les dépendances : 
   ```bash
   rm -rf node_modules
   npm install
   ```

3. Vérifier les erreurs TypeScript : `npm run lint`
4. Vérifier la version de Node.js (18+)

## Problèmes de performance

### Symptôme
```
Slow page loads
High memory usage
```

### Solutions
1. Vérifier la taille des bundles : `npm run build`
2. Optimiser les images
3. Vérifier les requêtes API inutiles
4. Utiliser React.memo pour les composants lourds
