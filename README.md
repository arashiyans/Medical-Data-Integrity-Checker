# Medical Data Integrity Checker  

**Medical Data Integrity Checker** is a PyQt5-based desktop application designed to securely store and verify the integrity of patient medical records. It employs advanced encryption and hashing techniques to ensure data confidentiality and integrity.  

## 📋 Features  
### 🛡️ Security Features  
- **ChaCha20 Encryption**: Protects patient data with a secure 256-bit key and nonce.  
  - Formula:  
    ```
    encrypted_data = ChaCha20_Encrypt(data, key, nonce)
    ```
- **SHA-256 Hashing**: Ensures data integrity by creating a unique hash for each record.  
  - Formula:  
    ```
    hash = SHA256(original_data)
    ```
- **Data Verification**: Compares stored hash with recalculated hash from the original file.  

### 🌟 User-Friendly Features  
- Simple and intuitive GUI for inputting and managing patient records.  
- Save encrypted patient data as text files.  
- Verify data integrity with a single click.  

## 🛠️ Technologies Used  
- **Programming Language**: Python  
- **GUI Framework**: PyQt5  
- **Encryption**: ChaCha20 from the `cryptography` library  
- **Hashing**: SHA-256 from the `hashlib` library  
- **Database**: MySQL (via `pymysql` library)  

## 📌 Requirements  
- Python 3.8 or higher  
- Libraries:  
  ```bash
  pip install PyQt5 cryptography pymysql
  ```  
- MySQL Server  

## ⚙️ Setup Instructions  
1. Clone the repository:  
   ```bash
   git clone <repository_url>
   cd MedicalDataIntegrityChecker
   ```  
2. Install the required libraries:  
   ```bash
   pip install -r requirements.txt
   ```  
3. Configure the MySQL database:  
   - Create a database named `rumahsakit`.  
   - Add a table `medical_records` with the following schema:  
     ```sql
     CREATE TABLE medical_records (
         id INT AUTO_INCREMENT PRIMARY KEY,
         name VARCHAR(255),
         encrypted_data TEXT,
         nonce VARCHAR(16),
         hash_sha256 VARCHAR(64)
     );
     ```  
4. Run the application:  
   ```bash
   python main.py
   ```  

## 📖 How It Works  
### Data Encryption  
- When saving patient data:  
  - A **nonce** (random 16-character alphanumeric string) is generated.  
  - The data is encrypted using the ChaCha20 algorithm:  
    ```
    encrypted_data = ChaCha20_Encrypt(original_data, key, nonce)
    ```
  - A SHA-256 hash of the original data is calculated:  
    ```
    hash = SHA256(original_data)
    ```
  - Both encrypted data and hash are stored in the database.  

### Data Verification  
- When verifying a file:  
  - The file content is read and hashed:  
    ```
    calculated_hash = SHA256(file_content)
    ```
  - The hash is compared with the stored hash in the database.  
  - If the hashes match, the data is decrypted using ChaCha20:  
    ```
    decrypted_data = ChaCha20_Decrypt(encrypted_data, key, nonce)
    ```

## 📸 Screenshots  
(Include screenshots of the application UI here.)  

## 🚀 Future Enhancements  
- Cloud storage for secure backups.  
- Role-based authentication for better access control.  
- Enhanced logging for error tracking.  

## 📜 License  
This project is licensed under the MIT License.  

---
