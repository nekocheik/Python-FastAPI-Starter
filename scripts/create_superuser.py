#!/usr/bin/env python3
"""
Script pour créer un superutilisateur.
Usage: python scripts/create_superuser.py
"""
import sys
import os
import asyncio
from getpass import getpass

# Ajouter le répertoire parent au chemin de recherche pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate
from app.services.user import get_by_email, create_user


def get_input(prompt, required=True):
    value = input(prompt)
    while required and not value:
        print("Cette valeur est requise.")
        value = input(prompt)
    return value


async def create_superuser():
    print("Création d'un superutilisateur")
    print("-----------------------------")

    # Obtenir les informations utilisateur
    email = get_input("Email: ")
    full_name = get_input("Nom complet: ", required=False)
    
    # Obtenir le mot de passe et le confirmer
    while True:
        password = getpass("Mot de passe: ")
        if not password:
            print("Le mot de passe est requis.")
            continue
        
        password_confirm = getpass("Confirmer le mot de passe: ")
        if password != password_confirm:
            print("Les mots de passe ne correspondent pas. Essayez à nouveau.")
            continue
        break

    # Créer l'utilisateur
    db = SessionLocal()
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = get_by_email(db, email=email)
        if existing_user:
            print(f"Un utilisateur avec l'email '{email}' existe déjà.")
            return

        # Créer l'utilisateur
        user_in = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_superuser=True,
        )
        user = create_user(db, user_in=user_in)
        print(f"Superutilisateur '{user.email}' créé avec succès!")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(create_superuser()) 