from hashlib import sha512

def generate_password(password):
    # Mengenkripsi password menggunakan SHA-256
    hashed_password = hashlib.sha512(password.encode()).hexdigest()
    return hashed_password

# Meminta input password dari pengguna
password = input("Masukkan password: ")

# Membuat password terenkripsi
hashed_password = generate_password(password)

# Menampilkan password terenkripsi
print("Password terenkripsi: ", hashed_password)