# NSC_Semester_Project
# Blockchain-Based Secure E-Voting System

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg)
![Cryptography](https://img.shields.io/badge/Security-RSA%20%26%20SHA--256-success.svg)

##  Project Overview
[cite_start]Electronic voting systems are becoming popular, but traditional systems are often centralized and vulnerable to hacking, vote tampering, and a lack of transparency[cite: 22]. [cite_start]This project is a **Blockchain-Based Secure E-Voting System** designed to ensure secure, transparent, and verifiable digital voting[cite: 24]. 

[cite_start]By combining a decentralized blockchain architecture with cryptographic techniques, this system mitigates the risks of traditional e-voting, including centralized control, vote manipulation, and the possibility of double voting[cite: 26, 27, 28, 30].

## Key Objectives
* Design a decentralized blockchain-based voting architecture[cite: 33].
* Implement **SHA-256 hashing** to maintain block integrity[cite: 34].
* Utilize **RSA-based digital signatures** for secure voter authentication[cite: 35].
* Strictly prevent duplicate (double) voting[cite: 36].
* Ensure total transparency and secure vote counting[cite: 37].

##  Tools & Technologies
* *Programming Language:** Python [cite: 39]
* *Web Framework:** Flask [cite: 39]
* *Cryptography:** RSA, SHA-256 [cite: 39]
* *Libraries:** `hashlib`, `cryptography`, `python-dotenv` [cite: 39]
* *Frontend:** HTML5, CSS3, JavaScript

##  Project Structure
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


Installation & Setup
1. Clone the repository:

Bash
git clone [https://github.com/your-username/e-voting-system.git](https://github.com/your-username/e-voting-system.git)
cd e-voting-system
2. Create and activate a virtual environment (Recommended):

Bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install dependencies:

Bash
pip install -r requirements.txt
4. Set up Environment Variables:

Create a file named .env in the root directory.

Copy the contents from .env.example (or use the configuration discussed previously) and add your secure keys.

5. Run the application:

Bash
flask run
# OR
python app.py
The system will be hosted locally at http://127.0.0.1:5000.

Academic Context
This project was developed as a Semester Project Proposal for the CIS311: Network Security and Cryptography course.


Institution: Daffodil International University (DIU) 
+1


Department: Computing And Information System 


Semester: Spring 2026 (6th semester) 

Developed By:
Md. Salman Ahmed (ID: 0242410012091024) 


Nazmul Prodhan (ID: 0242410012091030) 

Supervised By:
Dr. Md. Biplob Hossain Assistant Professor, Department of CIS 
