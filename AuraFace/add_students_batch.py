
import requests

API_URL = "http://localhost:8000/admin/students"
ADMIN_TOKEN = "your_admin_token_here" 

# Extracted from image excluding 23CSE540, 23CSE700, 23CSE706
students = [
    ("23CSE513", "PRIYANSHU GUPTA"),
    ("23CSE516", "MANAS RANJAN SETH"),
    ("23CSE519", "JEETANSHU SEKHAR SAHOO"),
    ("23CSE522", "ANSUMAN MAHAPATRA"),
    ("23CSE525", "U.GOPAL KRISHNA"),
    ("23CSE528", "BISWAJIT SAHOO"),
    ("23CSE531", "BISWAJEET PATRA"),
    ("23CSE534", "VIVEK KUMAR BEHERA"),
    ("23CSE537", "ADITYA PRATAP DEB"),
    # Excluded 23CSE540 (GAYATRI DHAL)
    ("23CSE543", "P ROHIT KUMAR SUBUDHI"),
    ("23CSE546", "RAHUL SRIBASTAB DAS"),
    ("23CSE549", "TAPAN KUMAR SAHOO"),
    ("23CSE553", "ABHISHEK SINGHANIA"),
    ("23CSE556", "SWASTIK PARICHA"),
    ("23CSE559", "SUMIT KUMAR BISWAL"),
    ("23CSE562", "ASHUTOSH SAHU"),
    ("23CSE565", "PRUTHIVIRAJ PRADHAN"),
    ("23CSE569", "SUPREETI DAS"),
    ("23CSE574", "SWAROOP MAHARANA"),
    ("23CSE577", "P.JAGANNATH DORA"),
    ("23CSE580", "RUDRA ABHISHEK BADATIA"),
    ("23CSE583", "AKANSHYA MUND"),
    ("23CSE586", "JAYA PRAKASH SAHOO"),
    ("23CSE589", "KHUSI NAYAK"),
    ("23CSE592", "SUBHENDU DAS"),
    ("23CSE596", "SATYAJIT ROUTRAY"),
    ("23CSE601", "ANKIT KUMAR"),
    ("23CSE605", "AYUSH RANJAN BISWAL"),
    ("23CSE609", "NISHIT MOHAPATRA"),
    ("23CSE612", "DEEPAK KUMAR"),
    ("23CSE615", "PIYUSH KUMAR TRIPATHY"),
    ("23CSE618", "SATYAPRIYA SAMANTARAYA"),
    ("23CSE623", "SWARUP NAYAK"),
    ("23CSE626", "ADITYA MAHARANA"),
    ("23CSE630", "TVS HARSHVARDHAN"),
    ("23CSE633", "J.CHANDRA SEKHAR REDDY"),
    ("23CSE636", "BANDANA SAHU"),
    ("23CSE639", "JYOTISANGAM BEHERA"),
    ("23CSE642", "T PRITI SUBUDHI"),
    ("23CSE645", "SWADESH SEKHAR SWAIN"),
    ("23CSE648", "RITESH RANJAN KHATUA"),
    ("23CSE651", "ELLORA DHAL"),
    ("23CSE654", "SATYAM SENAPATI"),
    ("23CSE660", "PRASAD PALEI"),
    ("23CSE663", "PRIYASA PATRO"),
    ("23CSE666", "BISWAJEET ROUT"),
    ("23CSE670", "ARYAN"),
    ("23CSE673", "STHITAPRAJNA ACHARYA"),
    ("23CSE676", "STHITAPRAGYAN DAS"),
    ("23CSE679", "AISHWORYA PANDA"),
    ("23CSE685", "SMRUTI RANJAN SENAPATI"),
    ("23CSE688", "PRATIK PRIYADARSHI"),
    ("23CSE691", "MANAS RANJAN MAHANTA"),
    ("23CSE694", "KISHOR HIAL"),
    ("23CSE697", "ZENITH POWELL MINJ"),
    # Excluded 23CSE700 (ARUN KUMAR BISOYI)
    ("23CSE703", "MRUNAL KANTA PARIDA"),
    # Excluded 23CSE706 (RANJEET SINGH BAGHEL)
]

# Get a token - Assuming local dev or replace manually
# Ideally we login first to get token.
def login(username, password):
    url = "http://localhost:8000/auth/login"
    data = {"username": username, "password": password}
    resp = requests.post(url, data=data)
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        print("Login failed:", resp.text)
        return None

token = login("temp_admin", "temp123")
if not token:
    exit()

headers = {"Authorization": f"Bearer {token}"}

for roll, name in students:
    data = {
        "name": name,
        "roll_no": roll,
        "department": "CSE",  # Assuming 23CSE implies CSE
        "year": 3,
        "section": "I",
        "semester": 6
    }
    
    # Check if exists first to avoid error spam? The API returns 400 if exists.
    try:
        resp = requests.post(API_URL + "/", data=data, headers=headers) # Using data= for Form data
        if resp.status_code == 200:
            print(f"Added {name} ({roll})")
        elif resp.status_code == 400 and "already exists" in resp.text:
            print(f"Skipped {name} ({roll}) - Already exists")
        else:
            print(f"Failed to add {name} ({roll}): {resp.text}")
    except Exception as e:
        print(f"Error adding {name}: {e}")
