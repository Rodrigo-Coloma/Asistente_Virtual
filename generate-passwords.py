import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Administrador", "Alvaro Avendaño", "Alvaro Lucas"]
usernames = ["admin", "aavendano", "alucas"]
passwords = ["$dm1n", "Ilu234", "Ilu234"]

hashed_passwords = stauth.Hasher(passwords)

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)