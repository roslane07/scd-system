from app.database import db
from app.models.personne import Personne
from app.utils.auth import hash_password

db.connect()

# Suppression de TOUS les Anciens et P3 existants
q = Personne.delete().where(Personne.role.in_(['ANCIEN', 'P3']))
q.execute()

STAFF = [
    # (Prenom, Nom, Buque, Nums, Role)
    ('alaa eddine', 'tahir', 'CHIRAC', '49-(1)°3', 'P3'),
    ('omar', 'boubou', 'ROS(BOÜ)2', '128', 'P3'),
    ('chaimaa', 'jouadri', 'titi', '132', 'P3'),
    ('mohamed', 'rhizlane', "dentit'ss", '36-154', 'P3'),
    
    ('yassmine', 'saadouni', 'Dentriss', '15', 'ANCIEN'),
    ('hafsa', 'essayhi', 'T’ila', '10', 'ANCIEN'),
    ('nabil', 'kardad', 'DenLotus', '5', 'ANCIEN'),
    ('fatima ezzahrae', 'aziz', 'Ta(z)°i(z)°illy', '16', 'ANCIEN'),
    ('mouhcine', 'mrizik', None, None, 'ANCIEN'),
    ('aymane', 'khodra', None, None, 'ANCIEN'),
]

added = 0
for prenom, nom, buque, nums, role in STAFF:
    suffix = '223' if role == 'P3' else '224'
    pwd = f'{nom}{suffix}'
    Personne.create(
        nom=nom,
        prenom=prenom,
        role=role,
        buque=buque,
        numero_fams=nums,
        password_hash=hash_password(pwd)
    )
    added += 1

print(f'✅ {added} accounts recreated perfectly.')
