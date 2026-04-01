import sys
import math
import getpass
import os
import json

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer


os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--log-level=3 --disable-gpu"

# --- CONFIG ---
USERNAME = input("Enter username: ")
PASSWORD = getpass.getpass("Enter password: ")
URL = "https://just-dice.com"

STATE_FILE = "bot_state.json"


# -------------------------------
# PERSISTENCE HELPERS
# -------------------------------
def save_state(data):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"⚠️ Failed to save state: {e}")


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return None


# -------------------------------
class RunBot:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.view = QWebEngineView()

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(layout)
        container.resize(1920, 1080)
        container.hide()

        self.view.load(QUrl(URL))
        self.view.hide()

        self.initialized = False

        print("✅ Page loaded")
        print("⏳ Waiting 35 seconds for full render...")
        QTimer.singleShot(35000, self.handle_popup)

        self.app.exec()

    # -------------------------------
    def handle_popup(self):
        print("🔧 Closing popup...")
        self.view.page().runJavaScript(
            'var c=document.querySelector(".fancybox-close"); if(c){c.click();}'
        )

        self.view.page().runJavaScript("""
        var links = document.querySelectorAll("a");
        for (let i = 0; i < links.length; i++) {
            if (links[i].innerText.trim() === "Account") {
               links[i].click();
               break;
             }
         }
         """)

        QTimer.singleShot(5000, self.do_login)

    def do_login(self):
        print("🔐 Logging in...")

        import json
        safe_user = json.dumps(USERNAME)
        safe_pass = json.dumps(PASSWORD)

        self.view.page().runJavaScript(f'document.querySelector("#myuser").value={safe_user};')
        self.view.page().runJavaScript(f'document.querySelector("#mypass").value={safe_pass};')

        self.run_js_click("#myok")

        print("⏳ Waiting for login...")
        QTimer.singleShot(20000, self.start_betting)

    # -------------------------------
    def start_betting(self):
        print("▶ Starting betting loop...")

        self.state = load_state()

        self.get_value("#pct_balance", self.init_betting)

    def init_betting(self, raw_bal):
        try:
            whiskers = float(raw_bal.replace(',', ''))
        except:
            print("❌ Failed to read balance")
            return

        self.whiskers = whiskers
        self.tabby = round(whiskers / 144000, 8)
        self.purr = 49.5
        self.tens = self.tabby * 10
        self.sevens = self.tabby * 6.9
        self.eights = self.tabby * 7.9
        self.mighty = math.floor(whiskers / self.tens) * self.tens

        if self.state:
            print("♻️ Restoring previous state...")
            self.cat = self.state.get("cat", self.tabby)
            self.felix = self.state.get("felix", self.mighty)
            self.orgy = self.state.get("orgy", self.mighty)
            self.shadow = self.state.get("shadow", whiskers)
            self.smokey = self.state.get("smokey", whiskers)
            self.fart = self.state.get("fart", 1)
        else:
            print("🆕 Starting fresh state...")
            self.cat = self.tabby
            self.fart = 1
            self.shadow = whiskers
            self.smokey = whiskers
            self.felix = float(self.mighty)
            self.orgy = float(self.mighty)

        print(f"🐾 Balance: {whiskers:.8f} | Bet: {self.cat:.8f}")

        self.run_js_click("#b_min")

        self.timer = QTimer()
        self.timer.timeout.connect(self.bet_step)
        self.timer.start(200)

    # -------------------------------
    def bet_step(self):
        self.get_value("#pct_balance", self.process_bet)

    def process_bet(self, curr_bal_str):
        try:
            actual_bal = float(curr_bal_str.replace(',', ''))

            if ((self.shadow == actual_bal) or (self.smokey == actual_bal)):

                current_jasper = actual_bal
                self.mighty = math.floor(current_jasper / self.tens) * self.tens

                if current_jasper >= (self.orgy + (self.tens * self.fart)):
                    self.cat = float(self.tabby)
                    self.fart = 1
                    self.felix = float(self.mighty)
                    self.orgy = float(self.mighty)

                if (current_jasper > (self.mighty + self.sevens)) and (current_jasper < (self.mighty + self.eights)) and current_jasper > self.felix:
                    self.cat *= 2
                    self.felix = float(current_jasper)

                if (current_jasper > (self.mighty + self.sevens)) and (current_jasper < (self.mighty + self.eights)) and current_jasper < self.felix:
                    self.cat *= 2
                    self.fart = 0
                    self.felix = float(current_jasper)

                print(f"📈 Bal: {actual_bal:.8f} | Profit: {actual_bal - self.whiskers:.8f} | Bet: {self.cat:.8f}")

                self.set_value("#pct_chance", self.purr)
                self.set_value("#pct_bet", f"{self.cat:.8f}")

                self.shadow = round(current_jasper + self.cat, 8)
                self.smokey = round(current_jasper - self.cat, 8)

                # 💾 SAVE STATE HERE
                save_state({
                    "cat": self.cat,
                    "felix": self.felix,
                    "orgy": self.orgy,
                    "shadow": self.shadow,
                    "smokey": self.smokey,
                    "fart": self.fart
                })

                self.run_js_click("#a_lo")

        except Exception as e:
            print(f"⚠️ Loop error: {e}")

    # -------------------------------
    def get_value(self, selector, callback):
        script = f'''
        (function() {{
            let el = document.querySelector("{selector}");
            return el ? el.value : "";
        }})();
        '''
        self.view.page().runJavaScript(script, callback)

    def set_value(self, selector, value):
        script = f'''
        var el = document.querySelector("{selector}");
        if(el) el.value = "{value}";
        '''
        self.view.page().runJavaScript(script)

    def run_js_click(self, selector):
        script = f'''
        var el = document.querySelector("{selector}");
        if(el) el.click();
        '''
        self.view.page().runJavaScript(script)


# -------------------------------
if __name__ == "__main__":
    RunBot()