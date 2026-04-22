import time
import json
import math
import getpass
from datetime import datetime
from decimal import Decimal, getcontext

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Satoshi precision
getcontext().prec = 20

# --- CONFIG ---
USERNAME = input("Enter username: ")
PASSWORD = getpass.getpass("Enter password: ")
URL = "https://just-dice.com"
STATE_FILE = "bot_state.json"

def save_state(data):
    try:
        serializable = {k: str(v) if isinstance(v, Decimal) else v for k, v in data.items()}
        with open(STATE_FILE, "w") as f:
            json.dump(serializable, f)
    except Exception: pass

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            # Added next_compound to tracked keys
            keys = ["cat", "felix", "orgy", "shadow", "smokey", "tracked_balance", "initial_balance", "last_balance", "next_compound"]
            for k in keys:
                if k in data: data[k] = Decimal(data[k])
            return data
    except: return None

class RunBot:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.binary_location = "/home/snowy/waterfox/waterfox"
        service = Service("/home/snowy/geckodriver")
        self.driver = webdriver.Firefox(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        self.last_activity_time = time.time()

    def start(self):
        print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Page loading...")
        self.driver.get(URL)
        time.sleep(10)
        
        # Clear fancybox overlays
        self.driver.execute_script("document.querySelectorAll('.fancybox-overlay').forEach(e => e.remove());")
        
        try:
            acc_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Account')]")))
            self.driver.execute_script("arguments[0].click();", acc_link)
        except: pass

        self.wait.until(EC.presence_of_element_located((By.ID, "myuser")))
        self.driver.find_element(By.ID, "myuser").send_keys(USERNAME)
        self.driver.find_element(By.ID, "mypass").send_keys(PASSWORD)
        print("⏳ Logging in...")
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.ID, "myok"))
        time.sleep(15)

        while True:
            bal_str = self.driver.find_element(By.ID, "pct_balance").get_attribute("value")
            if bal_str:
                self.setup_and_jumpstart(Decimal(bal_str))
                break
            time.sleep(1)

    def calculate_units(self, balance):
        """Helper to set strategy units based on a balance amount"""
        self.tabby = (balance / Decimal("144000")).quantize(Decimal("1.00000000"))
        self.tens = self.tabby * 10
        self.sevens = self.tabby * Decimal("6.9")
        self.eights = self.tabby * Decimal("7.9")

    def setup_and_jumpstart(self, real_bal):
        self.calculate_units(real_bal)
        
        self.state = load_state()
        if self.state:
            print("📂 [RECOVERY] Resuming state...")
            self.cat = self.state["cat"]
            self.felix = self.state["felix"]
            self.orgy = self.state["orgy"]
            self.fart = self.state["fart"]
            self.initial_balance = self.state.get("initial_balance", real_bal)
            self.next_compound = self.state.get("next_compound", real_bal * Decimal("2.4"))
            
            # Drift correction
            drift = real_bal - self.state.get("last_balance", real_bal)
            self.tracked_balance = self.state.get("tracked_balance", real_bal) + drift
        else:
            print("🆕 Fresh start.")
            self.cat = self.tabby
            self.fart = 1
            self.tracked_balance = self.initial_balance = real_bal
            self.next_compound = real_bal * Decimal("2.4")
            mighty = (math.floor(real_bal / self.tens)) * self.tens
            self.felix = self.orgy = mighty

        self.last_balance = real_bal
        self.last_activity_time = time.time()
        
        print(f"📈 Next Compound Milestone: {self.next_compound:.8f}")
        print("🚀 JUMPSTART: Firing initial bet...")
        self.fire_bet()

    def fire_bet(self):
        """Sets UI and triggers Lo button"""
        self.driver.execute_script(f'document.querySelector("#pct_chance").value="49.5";')
        self.driver.execute_script(f'document.querySelector("#pct_bet").value="{self.cat:.8f}";')
        
        # Sync target shadows
        self.shadow = (self.last_balance + self.cat).quantize(Decimal("1.00000000"))
        self.smokey = (self.last_balance - self.cat).quantize(Decimal("1.00000000"))
        
        btn = self.driver.find_element(By.ID, "a_lo")
        self.driver.execute_script("arguments[0].click();", btn)

    def tick(self):
        if time.time() - self.last_activity_time > 120:
            print("⚠️ Watchdog: No activity.")
            return False

        try:
            bal_str = self.driver.find_element(By.ID, "pct_balance").get_attribute("value")
            if not bal_str: return True
            current_real = Decimal(bal_str)
        except: return True

        if current_real != self.last_balance:
            delta = current_real - self.last_balance
            
            # --- THE HACKER / DRIFT GUARD ---
            # Using abs() is a cleaner way to check both positive and negative jumps
            if abs(delta) > (self.cat * Decimal("1.01")): # 1% margin for small site fees/rounding
                print(f"🕒 [{datetime.now().strftime('%H:%M:%S')}] ⚠️ UNEXPECTED DELTA: {delta:+.8f} (Expected ~{self.cat:.8f})")
                print("🚨 fuck off hacker")
                import sys
                sys.exit() # Hard stop
            
            self.tracked_balance += delta
            self.last_balance = current_real
            self.last_activity_time = time.time() 
            
            # Log with Bet (Cat) included
            print(f"🕒 [{datetime.now().strftime('%H:%M:%S')}] | Bal: {current_real:.8f} | Bet: {self.cat:.8f} | Delta: {delta:+.8f} | Life: {(self.tracked_balance - self.initial_balance):+.8f}")

            # ... (Rest of Strategy and Compounding) ...

            # --- COMPOUNDING ---
            if self.tracked_balance >= self.next_compound:
                print(f"💎 [COMPOUND] Milestone hit! Re-upping base bets.")
                self.calculate_units(self.tracked_balance)
                self.next_compound = self.tracked_balance * Decimal("2.4")
                self.cat = self.tabby # Reset cat to new higher tabby
                print(f"📊 New Tabby: {self.tabby:.8f} | Target: {self.next_compound:.8f}")

            # --- STRATEGY ---
            mighty = (math.floor(self.tracked_balance / self.tens)) * self.tens
            
            # Reset logic
            if self.tracked_balance >= (self.orgy + (self.tens * self.fart)):
                self.cat, self.fart = self.tabby, 1
                self.felix = self.orgy = mighty
            # Multiplier zones
            in_zone = (mighty + self.sevens) < self.tracked_balance < (mighty + self.eights)
            
            if in_zone:
                    if self.tracked_balance < self.felix:
                        self.fart = 0
                        self.cat *= 2
                        self.felix = self.tracked_balance
                    elif self.tracked_balance > self.felix:
                        self.cat *= 2
                        self.felix = self.tracked_balance



            save_state({
                "cat": self.cat, "felix": self.felix, "orgy": self.orgy, "fart": self.fart,
                "tracked_balance": self.tracked_balance, "initial_balance": self.initial_balance,
                "last_balance": self.last_balance, "next_compound": self.next_compound
            })
            
            self.fire_bet()

        return True

if __name__ == "__main__":
    while True:
        bot = RunBot()
        try:
            bot.start()
            while bot.tick():
                time.sleep(0.1)
        except KeyboardInterrupt: break
        except Exception as e: print(f"💥 Error: {e}")
        finally:
            bot.driver.quit()
            time.sleep(5)
