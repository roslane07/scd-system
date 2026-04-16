import sys
import os

# Set PYTHONPATH internally
sys.path.append('/app')

from app.database import db
from app.models.personne import Personne
from app.utils.constants import ROLE_P3

def set_admin(identifier):
    try:
        # Try to find by nom first, then by buque
        user = None
        try:
            user = Personne.get(Personne.nom ** identifier)
        except Personne.DoesNotExist:
            try:
                user = Personne.get(Personne.buque == identifier)
            except Personne.DoesNotExist:
                pass
        
        if not user:
            print(f"User {identifier} not found by nom or buque.")
            return

        user.role = ROLE_P3
        user.save()
        print(f"Successfully updated {user.nom} {user.prenom} (Buque: {user.buque}) to P3")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_admin.py <username_or_buque>")
    else:
        db_path = os.environ.get("SCD_DATABASE_PATH", "/data/scd.db")
        db.init(db_path)
        set_admin(sys.argv[1])
