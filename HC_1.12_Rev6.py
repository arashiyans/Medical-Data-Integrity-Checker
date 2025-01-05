import sys 
import hashlib
import pymysql
import os
import secrets
import string
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDateEdit, QFileDialog
from PyQt5.QtGui import QPixmap 
from PyQt5.QtCore import Qt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.backends import default_backend

class MedicalDataIntegrityChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.key = b"1234567890abcdef1234567890abcdef"  # Kunci 256-bit untuk ChaCha20
        self.nonce = self.generate_nonce()  # Generate nonce 16 karakter yang berisi angka dan huruf

    def initUI(self):
        self.setWindowTitle('Heaven Care Hospital')
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout()

        # Add logo
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap('medic.png').scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)

        # A. Identitas Pasien
        self.label_name = QLabel('Nama Pasien:')
        layout.addWidget(self.label_name)
        self.entry_name = QLineEdit(self)
        layout.addWidget(self.entry_name)

        self.label_address = QLabel('Alamat Pasien:')
        layout.addWidget(self.label_address)
        self.entry_address = QLineEdit(self)
        layout.addWidget(self.entry_address)

        self.label_age = QLabel('Umur Pasien:')
        layout.addWidget(self.label_age)
        self.entry_age = QLineEdit(self)
        layout.addWidget(self.entry_age)

        # B. Tanggal Pemeriksaan
        self.label_date = QLabel('Tanggal Pemeriksaan:')
        layout.addWidget(self.label_date)
        self.date_picker = QDateEdit(self)
        self.date_picker.setCalendarPopup(True)
        layout.addWidget(self.date_picker)

        # C. Diagnosis
        self.label_diagnosis = QLabel('Diagnosis:')
        layout.addWidget(self.label_diagnosis)
        self.entry_diagnosis = QLineEdit(self)
        layout.addWidget(self.entry_diagnosis)

        # D. Pengobatan dan/atau Tindakan
        self.label_treatment = QLabel('Pengobatan dan/atau Tindakan:')
        layout.addWidget(self.label_treatment)
        self.entry_treatment = QLineEdit(self)
        layout.addWidget(self.entry_treatment)

        # Generate and Verify buttons
        self.btn_generate = QPushButton('Generate and Save Data', self)
        self.btn_generate.clicked.connect(self.generate_and_save_data)
        layout.addWidget(self.btn_generate)

        self.btn_verify = QPushButton('Verify Data Integrity', self)
        self.btn_verify.clicked.connect(self.select_file_for_verification)
        layout.addWidget(self.btn_verify)

        self.setLayout(layout)

    def connect_db(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='rumahsakit'
        )

    def encrypt_chacha20(self, data):
        cipher = Cipher(algorithms.ChaCha20(self.key, self.nonce.encode()), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(data.encode()) + encryptor.finalize()

    def generate_nonce(self):
        characters = string.ascii_letters + string.digits  # Kombinasi angka dan huruf
        return ''.join(secrets.choice(characters) for _ in range(16))

    def generate_and_save_data(self):
        self.nonce = self.generate_nonce()  # Generate nonce baru setiap kali enkripsi
        name = self.entry_name.text()
        address = self.entry_address.text()
        age = self.entry_age.text()
        date = self.date_picker.date().toString(Qt.ISODate)
        diagnosis = self.entry_diagnosis.text()
        treatment = self.entry_treatment.text()

        if not all([name, address, age, date, diagnosis, treatment]):
            QMessageBox.warning(self, "Isi semua dulu ya")
            return

        # Menggabungkan data pasien
        original_data = f"Nama: {name}\nAlamat: {address}\nUmur: {age}\nTanggal: {date}\nDiagnosa: {diagnosis}\nPenanganan: {treatment}"
        
        # Encrypt data dengan ChaCha20 dan hash dengan SHA-256
        encrypted_data = self.encrypt_chacha20(original_data).hex()
        hashed_data = hashlib.sha256(original_data.encode()).hexdigest()

        # Menyimpan data ke file .txt
        file_name = f"{name}_data_pasien.txt"
        with open(file_name, 'w') as file:
            file.write(original_data)

        # Debugging: Pastikan data yang dienkripsi adalah dalam format hex
        print(f"Encrypted Data: {encrypted_data}")

        # Simpan data ke database
        try:
            connection = self.connect_db()
            with connection.cursor() as cursor:
                # Menyimpan data yang dienkripsi dan hash ke dalam database
                sql_medical_record = "INSERT INTO medical_records (name, encrypted_data, nonce, hash_sha256) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_medical_record, (name, encrypted_data, self.nonce, hashed_data))

            connection.commit()
            QMessageBox.information(self, "Success", "Data has been saved to the database.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save data to the database: {str(e)}")
        finally:
            connection.close()

        # Reset input fields
        self.entry_name.clear()
        self.entry_address.clear()
        self.entry_age.clear()
        self.entry_diagnosis.clear()
        self.entry_treatment.clear()
        self.date_picker.setDate(self.date_picker.minimumDate())

    def select_file_for_verification(self):
        # Membuka dialog untuk memilih file .txt
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Patient Data File", "", "Text Files (*.txt)", options=options)
        if file_path:
            self.verify_data_integrity(file_path)

    def verify_data_integrity(self, file_path):
        # Membaca isi file .txt
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Could not read file: {str(e)}")
            return

        # Menghitung hash dari isi file
        calculated_hash = hashlib.sha256(file_content.encode()).hexdigest()

        # Mengambil hash dari database untuk mencocokkan
        try:
            connection = self.connect_db()
            with connection.cursor() as cursor:
                # Query berdasarkan nama file yang sesuai dengan nama pasien
                patient_name = file_path.split('/')[-1].split('_')[0]
                sql_query = "SELECT name, encrypted_data, hash_sha256 FROM medical_records WHERE name = %s"
                cursor.execute(sql_query, (patient_name,))
                result = cursor.fetchone()

                if result:
                    stored_hash = result[2]
                    if stored_hash == calculated_hash:
                        # Decrypt data yang disimpan, periksa jika formatnya hex terlebih dahulu
                        decrypted_data = self.decrypt_chacha20(result[1])

                        # Menampilkan data pasien dalam popup jika hash cocok
                        QMessageBox.information(self, "Verification Success", f"Data cocok:\n\n{decrypted_data}")
                    else:
                        QMessageBox.warning(self, "Verification Failed", "The data has been tampered with!")
                else:
                    QMessageBox.warning(self, "Patient Not Found", "No data found for the specified patient.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve data from the database: {str(e)}")
        finally:
            connection.close()

    def decrypt_chacha20(self, encrypted_data):
        try:
            encrypted_bytes = bytes.fromhex(encrypted_data)
            cipher = Cipher(algorithms.ChaCha20(self.key, self.nonce.encode()), mode=None, backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
            return decrypted_data.decode()
        except ValueError as e:
            QMessageBox.critical(self, "Decryption Error", f"Sepertinya ada perubahan pada database: {str(e)}")
            return ""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MedicalDataIntegrityChecker()
    window.show()
    sys.exit(app.exec_())
