#!/usr/bin/env python3
"""
Add missing P3s and Anciens with correct family numbers.
"""
import sys
sys.path.insert(0, '/app')

from app.models.personne import Personne
from app.utils.auth import hash_password
from app.utils.constants import ROLE_P3, ROLE_ANCIEN

# Missing P3s to add
P3_TO_ADD = [
    {"nom": "defaa", "prenom": "Ayoub", "numero_fams": "33-34-76", "password": "defaa225"},
    {"nom": "FALOUSSE", "prenom": "Salah-eddine", "numero_fams": "144", "password": "falous225"},
    {"nom": "AKKAZI", "prenom": "Abderrahmane", "numero_fams": "95-111-47", "password": "akkazi225"},
    {"nom": "EL MAHDAOUI", "prenom": "Mohamed Salim", "numero_fams": "81-21", "password": "mahdaoui225"},
]

# Missing Anciens to add
ANCIENS_TO_ADD = [
    {"nom": "BOULAMI", "prenom": "Abderrahmane", "numero_fams": "128", "password": "boulami225", "parent_id": None},  # Fillot of Boubou Omar
    {"nom": "BELLAMINE", "prenom": "Kawtar", "numero_fams": "128", "password": "bellamine225", "parent_id": None},  # Fillot of Boubou Omar
]

def main():
    print("🔧 Adding missing P3s and Anciens...\n")
    
    # Add P3s
    for p3_data in P3_TO_ADD:
        try:
            # Check if already exists
            existing = Personne.select().where(
                Personne.nom == p3_data["nom"],
                Personne.prenom == p3_data["prenom"]
            ).first()
            
            if existing:
                print(f"⏭️  P3 already exists: {p3_data['prenom']} {p3_data['nom']} (id={existing.id})")
                # Update numero_fams if wrong
                if existing.numero_fams != p3_data["numero_fams"]:
                    existing.numero_fams = p3_data["numero_fams"]
                    existing.save()
                    print(f"   ✅ Updated numero_fams: {existing.numero_fams} → {p3_data['numero_fams']}")
                continue
            
            # Create P3
            p3 = Personne.create(
                nom=p3_data["nom"],
                prenom=p3_data["prenom"],
                numero_fams=p3_data["numero_fams"],
                role=ROLE_P3,
                password_hash=hash_password(p3_data["password"]),
                first_login=True,
            )
            print(f"✅ Created P3: {p3_data['prenom']} {p3_data['nom']} (id={p3.id}, numero_fams={p3_data['numero_fams']})")
        except Exception as e:
            print(f"❌ Error creating P3 {p3_data['prenom']} {p3_data['nom']}: {e}")
    
    print()
    
    # Find Boubou Omar (parent for the new anciens)
    try:
        boubou = Personne.get(Personne.nom.contains("BOUBOU"), Personne.role == ROLE_P3)
        print(f"Found parent P3: {boubou.prenom} {boubou.nom} (id={boubou.id})")
    except Personne.DoesNotExist:
        boubou = None
        print("⚠️  Boubou Omar not found, anciens will have no parent")
    
    # Add Anciens
    for ancien_data in ANCIENS_TO_ADD:
        try:
            # Check if already exists
            existing = Personne.select().where(
                Personne.nom == ancien_data["nom"],
                Personne.prenom == ancien_data["prenom"]
            ).first()
            
            if existing:
                print(f"⏭️  Ancien already exists: {ancien_data['prenom']} {ancien_data['nom']} (id={existing.id})")
                # Update numero_fams if wrong
                if existing.numero_fams != ancien_data["numero_fams"]:
                    existing.numero_fams = ancien_data["numero_fams"]
                    existing.save()
                    print(f"   ✅ Updated numero_fams: {existing.numero_fams} → {ancien_data['numero_fams']}")
                # Update parent if needed
                if boubou and (not existing.parent_id or existing.parent_id != boubou.id):
                    existing.parent_id = boubou.id
                    existing.save()
                    print(f"   ✅ Updated parent to Boubou Omar")
                continue
            
            # Create Ancien
            ancien = Personne.create(
                nom=ancien_data["nom"],
                prenom=ancien_data["prenom"],
                numero_fams=ancien_data["numero_fams"],
                role=ROLE_ANCIEN,
                parent_id=boubou.id if boubou else None,
                password_hash=hash_password(ancien_data["password"]),
                first_login=True,
            )
            print(f"✅ Created Ancien: {ancien_data['prenom']} {ancien_data['nom']} (id={ancien.id}, parent={boubou.prenom if boubou else 'none'})")
        except Exception as e:
            print(f"❌ Error creating Ancien {ancien_data['prenom']} {ancien_data['nom']}: {e}")
    
    # Update existing anciens with correct family numbers
    print("\n🔧 Updating existing anciens with correct family numbers...")
    
    ANCIEN_UPDATES = [
        {"nom": "EL JAMIAI", "prenom": "Yasser", "numero_fams": "36-154"},
        {"nom": "GAINOU", "prenom": "Maroua", "numero_fams": "49-13"},
        {"nom": "EL FILALI", "prenom": "Yassine", "numero_fams": "95-111-47"},
        {"nom": "EL HICHO", "prenom": "Ahmed", "numero_fams": "144"},
        {"nom": "KORCHI", "prenom": "Rana", "numero_fams": "33-34-76"},
        {"nom": "TARGUI", "prenom": "Marouane", "numero_fams": "33-34-76"},
        {"nom": "ASSMINA", "prenom": "Mohamed Amine", "numero_fams": "81-21"},
        {"nom": "ELABIBI", "prenom": "Saffa", "numero_fams": "36-154"},
        {"nom": "MRIZIK", "prenom": "Mouhcine", "numero_fams": "132"},
        {"nom": "KHODRA", "prenom": "Mohamed-aymane", "numero_fams": "95-111-47"},
        {"nom": "KARDAD", "prenom": "Nabil", "numero_fams": "36-154"},
        {"nom": "AZIZ", "prenom": "Fatima Zahra", "numero_fams": "144"},
        {"nom": "SAADOUNI", "prenom": "Yassmine", "numero_fams": "36-154"},
        {"nom": "ES-SAYHI", "prenom": "Hafsa", "numero_fams": "132"},
    ]
    
    for update in ANCIEN_UPDATES:
        try:
            ancien = Personne.get(Personne.nom.contains(update["nom"]), Personne.prenom.contains(update["prenom"]))
            old_num = ancien.numero_fams
            ancien.numero_fams = update["numero_fams"]
            ancien.save()
            print(f"✅ {ancien.prenom} {ancien.nom}: {old_num} → {update['numero_fams']}")
        except Personne.DoesNotExist:
            print(f"❌ Not found: {update['prenom']} {update['nom']}")
        except Exception as e:
            print(f"❌ Error updating {update['prenom']} {update['nom']}: {e}")
    
    print("\n📊 Done!")

if __name__ == "__main__":
    main()
