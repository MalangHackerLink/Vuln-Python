## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/Awasefra/vuln-python.git
cd nama-repo
```

### 2. Buat Virtual Environment (Opsional tapi Disarankan)

```bash
python -m venv venv
```

### 3. Aktifkan Virtual Environment

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Jalankan Aplikasi Flask

```bash
python app.py
```
## Postman Collection
[python vuln.postman_collection.json](https://github.com/user-attachments/files/20456122/python.vuln.postman_collection.json)

## Postman Environtment
[vul_environtment.postman_environment.json](https://github.com/user-attachments/files/20456138/vul_environtment.postman_environment.json)

### List VULN
- VULN 1: Secret Key Lemah dan Hardcoded (config.py)
- VULN 2: JWT Secret Key Lemah dan Hardcoded (config.py)
- VULN 3: Brute-force Login Tanpa Rate Limiting (auth_routes.py - /auth/login)
- VULN 4: Mass Assignment pada is_admin (models.py, auth_routes.py - /auth/register, /api/admin/users)
- VULN 5: Sensitive Data Exposure (Password Hash di User.to_dict) (models.py, auth_routes.py - /auth/profile, /api/admin/users)
- VULN 6: JWT Secret Key Lemah/Terbuka (Bagian dari VULN 2) (auth_routes.py - create_jwt_token)
- VULN 7: JWT Algoritma None & Kurangnya Validasi Algoritma (auth_routes.py - verify_jwt_token)
- VULN 8: Kepercayaan Berlebihan pada Payload JWT (auth_routes.py - auth_required)
- VULN 9: Global Read for Notes (note_routes.py - get_notes)
- VULN 10: SQL Injection (Melalui Komentar Kode) (http://127.0.0.1:5000/api/notes/view) (POST JSON id)
- VULN 11: Insecure Direct Object Reference (IDOR) pada Catatan (note_routes.py - get_note, update_note, delete_note)
- VULN 12: Mass Assignment pada Catatan (note_routes.py - update_note)
- VULN 13: Admin Endpoint Bergantung pada JWT Payload (note_routes.py - /admin/users)
- VULN 14 & 15: Error Handling yang Terlalu Generik/Bocor (app.py - errorhandler)
- VULN 16: Debug Mode Aktif di Produksi
