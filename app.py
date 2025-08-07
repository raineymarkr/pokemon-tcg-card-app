from tcgdexsdk import TCGdex, Language
from PySide6.QtWidgets import QApplication, QLabel, QTreeWidget, QTreeWidgetItem, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, Slot
import sys, json, requests, os
from dotenv import load_dotenv

tcgdex = TCGdex('en')

totalnumcards = 0

load_dotenv()

login_url = os.getenv("LOGIN_URL")
upload_url = os.getenv("UPLOAD_URL")
download_url = os.getenv("DOWNLOAD_URL")
username = os.getenv("username")
password = os.getenv("password")

try:
    cards = tcgdex.set.getSync('Wisdom of Sea and Sky')
except Exception as e:
    print(e)

app = QApplication([])

main_window = QWidget()
layout = QVBoxLayout(main_window)

settings_window = QWidget()
settings_layout = QVBoxLayout(settings_window)

tree= QTreeWidget()
tree.setColumnCount(3)
tree.setHeaderLabels(['Name', 'Deck', 'Acquired?'])

ho_oh_card_names = [
    "Tangela",
    "Tangrowth",
    "Hoppip",
    "Skiploom",
    "Jumpluff",
    "Heracross",
    "Slugma",
    "Magcargo",
    "Magby",
    "Entei",
    "Ho-oh ex",
    "Totodile",
    "Croconaw",
    "Feraligatr",
    "Marill",
    "Azumarill",
    "Delibird",
    "Ducklett",
    "Swanna",
    "Raikou",
    "Smoochum",
    "Togepi",
    "Togetic",
    "Togekiss",
    "Unown",
    "Girafarig",
    "Onix",
    "Gligar",
    "Gliscor",
    "Swinub",
    "Piloswine",
    "Mamoswine",
    "Phanpy",
    "Donphan ex",
    "Tyrogue",
    "Larvitar",
    "Pupitar",
    "Zubat",
    "Golbat",
    "Crobat ex",
    "Spinarak",
    "Ariados",
    "Umbreon ex",
    "Tyranitar",
    "Steelix",
    "Skarmory ex",
    "Klink",
    "Klang",
    "Klinklang",
    "Spearow",
    "Fearow",
    "Chansey",
    "Blissey",
    "Kangaskhan",
    "Sentret",
    "Furret",
    "Hoothoot",
    "Noctowl",
    "Teddiursa",
    "Ursaring",
    "Stantler",
    "Steel Apron",
    "Dark Pendant",
    "Silver",
    "Jasmine",
    "Hiker"
]

non_exclusive_card_names = [
    "Sunkern",
    "Sunflora",
    "Yanma",
    "Yanmega",
    "Pineco",
    "Cherubi",
    "Cherrim",
    "Darumaka",
    "Darmanitan",
    "Heatmor",
    "Emolga",
    "Jynx",
    "Snubbull",
    "Granbull",
    "Munna",
    "Musharna",
    "Sudowoodo",
    "Hitmontop",
    "Houndour",
    "Houndoom",
    "Absol",
    "Forretress",
    "Mawile",
    "Eevee",
    "Aipom",
    "Ambipom",
    "Dunsparce",
    "Bouffalant",
    "Rescue Scarf"
]

cardList = {}

cardNames = []
for card in cards.cards:
    if int(card.localId) < 202:
        if card.name in ho_oh_card_names:
            cardDeck = 'Ho-Oh'
        elif card.name in non_exclusive_card_names:
            cardDeck = 'Either'
        else:
            cardDeck = 'Lugia'
        cardList[card.name] = cardDeck
        cardNames.append(card.name)

totalnumcards = len(cardNames)
totalhooh = len(ho_oh_card_names)
totalnonexclusive = len(non_exclusive_card_names)
totallugia = totalnumcards - totalhooh - totalnonexclusive

aquiredLabel = QLabel("")

global jsonlist

@Slot()
def countCards():
    acquired_hooh = 0
    acquired_lugia = 0
    acquired_nonexclusive = 0
    jsonlist = {}

    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        deck = item.text(1)
        acquired = item.checkState(2) == Qt.Checked
        if acquired:
            if deck == 'Ho-Oh':
                acquired_hooh += 1
            elif deck == 'Lugia':
                acquired_lugia += 1
            else:
                acquired_nonexclusive += 1
        jsonlist[item] = acquired

    # Update the label's text instead of replacing the label
    aquiredLabel.setText(
        f"Ho-Oh: {acquired_hooh} / {totalhooh}<br>"
        f"Lugia: {acquired_lugia} / {totallugia}<br>"
        f"Non-Exclusive: {acquired_nonexclusive} / {totalnonexclusive}<br>"
        f"Total: {acquired_hooh + acquired_lugia + acquired_nonexclusive} / {totalhooh + totallugia + totalnonexclusive}"
    )





items = []

for key, value in cardList.items():
    item = QTreeWidgetItem([key, value, ""])
    item.setCheckState(2, Qt.Unchecked)
    items.append(item)

tree.insertTopLevelItems(0, items)

def login():
    params = {
        'username': username,
        'password': password
    }

    try:
        response = requests.post(login_url, json=params)

        if response.status_code == 200:
            response_data = response.json()
            token = response_data.get('access_token')
            if token:
                return token
            else:
                print("No token in response.")
        else:
            print("Login failed with status", response.status_code)
    except requests.exceptions.RequestException as e:
        print('Login request failed:', e)

    return None


@Slot()
def saveList():
    jsonlist = {}

    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        name = item.text(0)
        acquired = 1 if item.checkState(2) == Qt.Checked else 0
        jsonlist[name] = acquired

    jsonSaved = json.dumps(jsonlist, indent=2)
    
    try:
        # Write to disk
        with open("savedJson.txt", "w") as f:
            f.write(jsonSaved)

        # Upload file
        access = login()
        if not access:
            print("Save failed: no access token.")
            return

        headers = {
            'Authorization': f'Bearer {access}'
        }

        with open("savedJson.txt", "rb") as f:
            response = requests.post(upload_url, headers=headers, files={'file': f})
            print("Upload status:", response.status_code)
    except:
        print('Failed')

@Slot()
def loadList():
    try:
        access = login()
        if not access:
            print("Load failed: no access token.")
            return

        headers = {
            'Authorization': f'Bearer {access}'
        }

        r = requests.get(download_url, headers=headers)

        try:
            data = json.loads(r.content)  # ← use loads for string/bytes
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                name = item.text(0)
                if name in data:
                    state = Qt.Checked if data[name] == 1 else Qt.Unchecked
                    item.setCheckState(2, state)
        except Exception as e:
            print(f"Error loading saved list: {e}")
    except:
        print('Failed')


tree.insertTopLevelItems(0, items)

button = QPushButton("Count Totals")
button.clicked.connect(countCards)

settingsButton = QPushButton("Settings")
settingsButton.clicked.connect(settings_window.show)
saveButton = QPushButton("Save")
saveButton.clicked.connect(saveList)
loadButton = QPushButton("Load")
loadButton.clicked.connect(loadList)

layout.addWidget(tree)
layout.addWidget(button)
layout.addWidget(aquiredLabel)
layout.addWidget(settingsButton)

main_window.setLayout(layout)
main_window.setWindowTitle("TCGDex Card Tracker")
main_window.resize(600, 800)
main_window.show()

settings_layout.addWidget(saveButton)
settings_layout.addWidget(loadButton)

settings_window.setLayout(settings_layout)
settings_window.setWindowTitle("TCGDex Settings")
settings_window.resize(300, 400)




# label.show()
app.exec()

