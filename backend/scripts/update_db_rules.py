import sys
from app.database import db
from app.models.personne import Personne
from app.utils.auth import hash_password

db.connect()

print("Updating existing users passwords based on new rules...")
count = 0
users = list(Personne.select())
for p in users:
    if p.role == 'CONSCRIT':
        suffix = '225'
    elif p.role == 'ANCIEN':
        suffix = '224'
    elif p.role == 'P3':
        suffix = '223'
    else:
        continue
    
    pwd = f'{p.nom}{suffix}'
    p.password_hash = hash_password(pwd)
    p.save()
    count += 1

print(f"✅ {count} existing passwords updated.")

print("Adding requested true P3s and Anciens...")

STAFF = [
    # P3
    ("alaa eddine tahir", "CHIRAC", "49-(1)°3", "P3"),
    ("omar boubou", "ROS(BOÜ)2", "128", "P3"),
    ("chaimaa jouadri", "titi", "132", "P3"),
    # Anciens
    ("yassmine saadouni", "Dentriss", "15", "ANCIEN"),
    ("hafsa essayhi", "T’ila", "10", "ANCIEN"),
    ("nabil kardad", "DenLotus", "5", "ANCIEN"),
    ("fatima ezzahrae aziz", "Ta(z)°i(z)°illy", "16", "ANCIEN"),
]

added = 0
for nom, buque, nums, role in STAFF:
    # Check if exists
    if not Personne.get_or_none(Personne.nom == nom):
        suffix = '223' if role == 'P3' else '224'
        Personne.create(
            nom=nom,
            prenom="",
            role=role,
            buque=buque,
            numero_fams=nums,
            password_hash=hash_password(f"{nom}{suffix}")
        )
        added += 1

print(f"✅ {added} real staff accounts created.")

