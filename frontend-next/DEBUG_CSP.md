# 🔍 Debug Content Security Policy

## Problème Résolu : CSP bloque les connexions

### Correction Appliquée

La directive `connect-src` a été ajoutée dans `next.config.js` pour autoriser les connexions vers le backend.

### Vérifications

1. **Redémarrer Next.js** après modification de `next.config.js` ✅
   - Le serveur a détecté le changement et redémarré automatiquement

2. **Vider le cache du navigateur**
   - Appuyez sur `Ctrl+Shift+R` (Windows/Linux) ou `Cmd+Shift+R` (Mac)
   - Ou ouvrez les DevTools > Network > Cocher "Disable cache"

3. **Vérifier la CSP dans les headers**
   - Ouvrez DevTools > Network
   - Cliquez sur une requête
   - Vérifiez l'onglet "Headers"
   - Cherchez "Content-Security-Policy"
   - Elle devrait contenir : `connect-src 'self' http://localhost:8000 ...`

### Test Manuel dans la Console

Ouvrez la console du navigateur (F12) et testez :

```javascript
// Test 1: Vérifier l'URL de l'API
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

// Test 2: Test de connexion directe
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(data => console.log('Health check OK:', data))
  .catch(err => console.error('Health check FAILED:', err));

// Test 3: Test de login
const formData = new URLSearchParams();
formData.append('username', 'admin');
formData.append('password', 'admin123');

fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: formData.toString(),
})
  .then(r => r.json())
  .then(data => console.log('Login OK:', data))
  .catch(err => console.error('Login FAILED:', err));
```

### Si le Problème Persiste

1. **Vérifier que le backend tourne** :
   ```powershell
   curl http://localhost:8000/health
   ```

2. **Vérifier les CORS du backend** :
   - Le backend doit autoriser `http://localhost:3000` dans `ALLOWED_HOSTS`

3. **Vérifier les variables d'environnement** :
   - Ouvrez `frontend-next/.env.local`
   - Vérifiez que `NEXT_PUBLIC_API_URL=http://localhost:8000`

4. **Redémarrer complètement** :
   ```powershell
   # Arrêter Next.js (Ctrl+C)
   # Supprimer le cache
   cd frontend-next
   Remove-Item -Recurse -Force .next
   # Redémarrer
   npm run dev
   ```

### Configuration CSP Actuelle

```javascript
connect-src 'self' http://localhost:8000 ws://localhost:*
```

Cela autorise :
- ✅ Connexions vers le même domaine (`'self'`)
- ✅ Connexions vers `http://localhost:8000` (backend)
- ✅ WebSocket vers `localhost` (hot-reload)

