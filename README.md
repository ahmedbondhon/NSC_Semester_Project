# NSC_Semester_Project
# Blockchain-Based Secure E-Voting System

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg)
![Cryptography](https://img.shields.io/badge/Security-RSA%20%26%20SHA--256-success.svg)

## 📌 Project Overview
[cite_start]Electronic voting systems are becoming popular, but traditional systems are often centralized and vulnerable to hacking, vote tampering, and a lack of transparency[cite: 22]. [cite_start]This project is a **Blockchain-Based Secure E-Voting System** designed to ensure secure, transparent, and verifiable digital voting[cite: 24]. 

[cite_start]By combining a decentralized blockchain architecture with cryptographic techniques, this system mitigates the risks of traditional e-voting, including centralized control, vote manipulation, and the possibility of double voting[cite: 26, 27, 28, 30].

## 🎯 Key Objectives
* [cite_start]Design a decentralized blockchain-based voting architecture[cite: 33].
* [cite_start]Implement **SHA-256 hashing** to maintain block integrity[cite: 34].
* [cite_start]Utilize **RSA-based digital signatures** for secure voter authentication[cite: 35].
* [cite_start]Strictly prevent duplicate (double) voting[cite: 36].
* [cite_start]Ensure total transparency and secure vote counting[cite: 37].

## 🛠️ Tools & Technologies
* [cite_start]**Programming Language:** Python [cite: 39]
* [cite_start]**Web Framework:** Flask [cite: 39]
* [cite_start]**Cryptography:** RSA, SHA-256 [cite: 39]
* [cite_start]**Libraries:** `hashlib`, `cryptography`, `python-dotenv` [cite: 39]
* **Frontend:** HTML5, CSS3, JavaScript

## 📂 Project Structure
```text
e-voting-system/
│
├── app.py                 # Main Flask application
├── .env                   # Environment variables (Do not commit to GitHub!)
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
│
├── blockchain/            # Core blockchain backend
│   ├── __init__.py
│   ├── block.py           # Block structure and SHA-256 hashing
│   ├── blockchain.py      # Chain management and validation
│   └── wallet.py          # RSA key generation and digital signatures
│
├── templates/             # Frontend HTML templates
│   ├── base.html          
│   ├── index.html         # Homepage / Voter Login
│   ├── vote.html          # Secure voting ballot
│   └── dashboard.html     # Transparent vote verification
│
└── static/                # Static assets (CSS/JS)
    ├── css/style.css      
    └── js/main.js
