#!/usr/bin/env python3
"""
Update conscrits' numero_fams to match their P3 root's numero_fams.
This ensures the Fam's ranking shows correct family numbers.
"""
import sys
sys.path.insert(0, '/app')

from app.models.personne import Personne

def find_p3_root(person):
    """Climb the parent chain to find the P3 (root)."""
    current = person
    visited = set()
    
    while current.parent_id and current.id not in visited:
        visited.add(current.id)
        try:
            parent = Personne.get_by_id(current.parent_id)
            # P3 has no parent or role=P3
            if parent.role == 'P3' or not parent.parent_id:
                return parent
            current = parent
        except Personne.DoesNotExist:
            break
    return None

def main():
    print("🔧 Updating conscrits' numero_fams to match their P3 root...")
    
    conscrits = Personne.select().where(Personne.role == 'CONSCRIT')
    updated = 0
    skipped = 0
    
    for c in conscrits:
        p3 = find_p3_root(c)
        
        if p3:
            if p3.numero_fams:
                if c.numero_fams != p3.numero_fams:
                    old_num = c.numero_fams
                    c.numero_fams = p3.numero_fams
                    c.save()
                    updated += 1
                    print(f"  ✅ {c.prenom} {c.nom}: {old_num} → {p3.numero_fams}")
                else:
                    skipped += 1
                    print(f"  ⏭️  {c.prenom} {c.nom}: already correct ({c.numero_fams})")
            else:
                print(f"  ⚠️  {c.prenom} {c.nom}: P3 {p3.prenom} {p3.nom} has no numero_fams")
        else:
            print(f"  ⚠️  {c.prenom} {c.nom}: no P3 found (parent_id={c.parent_id})")
    
    print(f"\n📊 Summary:")
    print(f"   Updated: {updated} conscrits")
    print(f"   Skipped: {skipped} conscrits (already correct)")
    print(f"   Total: {updated + skipped} conscrits processed")

if __name__ == "__main__":
    main()
