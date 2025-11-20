#!/usr/bin/env python3
"""
Script pour générer les clés de sécurité
"""

import secrets
import sys
from pathlib import Path

def generate_keys():
    """Génère SECRET_KEY et ENCRYPTION_KEY"""
    secret_key = secrets.token_urlsafe(32)
    encryption_key = secrets.token_hex(32)
    
    print("=" * 60)
    print("🔑 Clés de sécurité générées")
    print("=" * 60)
    print(f"\nSECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print("\n" + "=" * 60)
    print("⚠️  Copiez ces valeurs dans votre fichier .env")
    print("=" * 60)
    
    # Optionnel : Mettre à jour automatiquement le fichier .env
    env_file = Path(".env")
    if env_file.exists():
        update_env = input("\nVoulez-vous mettre à jour automatiquement le fichier .env ? (o/n): ")
        if update_env.lower() == 'o':
            content = env_file.read_text()
            content = content.replace("SECRET_KEY=change-this-to-a-secure-random-string-min-32-chars", 
                                     f"SECRET_KEY={secret_key}")
            content = content.replace("ENCRYPTION_KEY=change-this-to-64-hex-characters-for-32-bytes-aes-256",
                                     f"ENCRYPTION_KEY={encryption_key}")
            env_file.write_text(content)
            print("✅ Fichier .env mis à jour avec succès !")
        else:
            print("📝 N'oubliez pas de mettre à jour manuellement votre fichier .env")
    else:
        print("⚠️  Fichier .env non trouvé. Créez-le d'abord avec : Copy-Item env.example .env")

if __name__ == "__main__":
    generate_keys()

