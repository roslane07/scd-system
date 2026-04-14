from app.database import db
from app.models.personne import Personne
from app.utils.auth import hash_password

RAW_NAMES = """SMANI Ayoub
KOUAME Christ Moh Hyemhand Aime Junior
AGOUDAR Aya
CHOUKRI Mohamed Amine
LAHYANI Osama
SAMODI Adam
ALIFRIQUI Zakaria
ETTABI Yasser
RAHEL Othmane
HANIF Alaa Eddine
ATARRAS Mohamed
ELBAKKOUCH Imane
EL FELLATI Nada
BOUHOU Ahmed
RABII Douae
EL BAGHDADI Mustapha
EL OUAHABI Ossama
BOUFADNA Chadi
ABOULHAOUL Yasser
GUEZNAI Adam
JAOUAD Abdelkbir
ENNHILA Bachchar
FELS Yassine
JLOK Mohamed
BEN MOUSSA Mohammed Amine
MOUNIR Hamza
BEN EL CADI Talal
BOLOU Dimi Zagadou Yann Derrick
CHARAHAYNE Nouhaila
SOLTANI Abderrahmane
ARABE Salma
ARHBAL Adam
SAWADOGO Nomwende Juste Placide
TALHI Fatima-ezzahra
DADA Salma
BENMANSOUR Fares
IKRADINE Youssef
MOURTAFIA Jamal Eddine
SALL Mouhamed
BOUCHAAB Ayoub
TOURE Omatara Aime
SANIE Bouchaib
EL KARMAOUI Mohamed Amine"""

lines = [l.strip() for l in RAW_NAMES.split('\n') if l.strip()]

db.connect()

# Delete placeholder conscrits
Personne.delete().where(Personne.role == 'CONSCRIT').execute()

added = 0
for line in lines:
    parts = line.split()
    nom_parts = [p for p in parts if p.isupper()]
    prenom_parts = [p for p in parts if not p.isupper()]
    
    # Exception handling if no uppercase or whatever
    if not nom_parts:
        nom_parts = [parts[0]]
        prenom_parts = parts[1:]
        
    nom = " ".join(nom_parts).lower()
    prenom = " ".join(prenom_parts).title()
    
    # Generate password: remove spaces and lowercase it + 225
    password_base = nom.replace(" ", "")
    pwd = f"{password_base}225"
    
    Personne.create(
        nom=nom,
        prenom=prenom,
        role='CONSCRIT',
        points_actuels=100,
        zone='ZONE_VERTE',
        password_hash=hash_password(pwd)
    )
    added += 1

print(f"✅ {added} conscrits réels recréés avec succès (mot de passe: nomattache225)!")
