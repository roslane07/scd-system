#!/usr/bin/env python3
"""
Update P3s' numero_fams with real family numbers.
"""
import sys
sys.path.insert(0, '/app')

from app.models.personne import Personne

# Mapping: P3 name → real numero_fams
P3_FAMS_MAPPING = {
    # P3s
    "RHIZLANE Mohamed": "36-154",
    "BOUBOU Omar": "128",
    "JOUADRI Chaimaa": "132",
    "TAHIR Alaa Eddine": "49-13",
    "defaa": "33-34-76",  # ayoub defaa
    "FALOUSSE Salah-eddine": "144",
    "AKKAZI Abderrahmane": "95-111-47",
    "EL MAHDAOUI Mohamed Salim": "81-21",
}

def find_p3_by_partial_name(name_part):
    """Find P3 by partial name match."""
    # Try exact match first
    try:
        p3 = Personne.get(
            (Personne.role == 'P3') & 
            (Personne.nom.contains(name_part) | Personne.prenom.contains(name_part))
        )
        return p3
    except Personne.DoesNotExist:
        pass
    
    # Try case-insensitive search
    for p3 in Personne.select().where(Personne.role == 'P3'):
        full_name = f"{p3.prenom} {p3.nom}".lower()
        if name_part.lower() in full_name:
            return p3
    
    return None

def main():
    print("🔧 Updating P3s' numero_fams with real family numbers...\n")
    
    updated = 0
    not_found = []
    
    for name_part, fams_number in P3_FAMS_MAPPING.items():
        p3 = find_p3_by_partial_name(name_part)
        
        if p3:
            old_num = p3.numero_fams
            p3.numero_fams = fams_number
            p3.save()
            updated += 1
            print(f"✅ {p3.prenom} {p3.nom}: {old_num} → {fams_number}")
        else:
            not_found.append(name_part)
            print(f"❌ P3 not found: {name_part}")
    
    print(f"\n📊 Summary:")
    print(f"   Updated: {updated} P3s")
    if not_found:
        print(f"   Not found: {not_found}")
    
    # Also update anciens who are P3 roots
    print("\n🔧 Updating Anciens with P3 role as family roots...")

if __name__ == "__main__":
    main()
