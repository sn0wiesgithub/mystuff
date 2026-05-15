import sys
import json
import math
import time
import getpass
import os
import logging
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QTextEdit)
from PyQt5.QtCore import QTimer, QUrl, Qt, QObject, pyqtSlot, QFile, QIODevice
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebChannel import QWebChannel

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-audio-output"
logging.getLogger("PyQt5").setLevel(logging.CRITICAL)

u = input("Enter username: ")
p = getpass.getpass("Enter password: ")

URL = "https://just-dice.com"
STATE_FILE = ".bot_state.json"


class WebBridge(QObject):
    def __init__(self, target_callback):
        super().__init__()
        self.target_callback = target_callback

    @pyqtSlot(str)
    def transmit_data(self, data_json):
        self.target_callback(data_json)


class BotEngine(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dice Native Bot (Infinite Flow)")
        self.resize(1024, 768)

        # --- INTERNAL STATE (Strictly Float) ---
        self.is_running = False
        self.last_balance = 0.0
        self.initial_balance = 0.0
        self.tracked_balance = 0.0
        self.next_compound = 0.0
        self.last_change_time = time.time()
        
        self.prev_balance = None
        self.prev_wins = None
        self.prev_losses = None
        
        self.cat = 0.0
        self.bolux = 0.0
        self.felix = 0.0
        self.orgy = 0.0
        self.fart = 1
        self.tabby = 0.0
        self.tens = 0.0
        self.sevens = 0.0
        self.eights = 0.0
        self.betfired = False
        self.shadow = 0.0
        self.shadowtwo = 0.0
        self.yay = 0.0
        self.growl = 0.0
        self.uppers = 6.9
        self.downers = 2.9
        
        # --- UI SETUP ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel)
        
        self.lbl_balance = QLabel("Balance: 0.00000000")
        self.lbl_profit = QLabel("Life Profit: 0.00000000")
        self.lbl_bet = QLabel("Next Bet: 0.00000000")
        self.lbl_compound = QLabel("Compound Goal: 0.00000000")
        
        left_layout.addWidget(self.lbl_balance)
        left_layout.addWidget(self.lbl_profit)
        left_layout.addWidget(self.lbl_bet)
        left_layout.addWidget(self.lbl_compound)
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background: #111; color: #0f0; font-family: monospace; font-size: 11px;")
        left_layout.addWidget(self.log_box)

        # Browser Setup
        self.browser_view = QWebEngineView()
        main_layout.addWidget(self.browser_view)
        
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

        self.channel = QWebChannel()
        self.bridge_object = WebBridge(self.evaluate_financial_sync)
        self.channel.registerObject("pyBridge", self.bridge_object)
        self.browser_view.page().setWebChannel(self.channel)

        # CRITICAL FIX: Automatically redeploy observer script anytime a page loads or reloads
        self.browser_view.loadFinished.connect(self.deploy_dom_observer)

        self.bet_in_flight = False
        self.last_activity_time = time.time()

        # Engine execution pulse loop timer
        self.engine_timer = QTimer()
        self.engine_timer.timeout.connect(self.process_tick)

        self.heartbeat = True
        self.log("System initialized. Booting engine view...")
        self.browser_view.setUrl(QUrl(URL))
        
        # First-time automatic kickoff sequence hook
        QTimer.singleShot(10000, self.kjool_look)

    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"[{ts}] {msg}")
        self.log_box.append(f"[{ts}] {msg}")

    def kjool_look(self):
        self.log("Analyzing interface state parameters...")
        self.betfired = False
        QTimer.singleShot(2000, self.inject_login)

    def inject_login(self):
        if not u or not p: return

        js = f"""
        (function() {{
            var usen = document.getElementById('myuser');
            var pasd = document.getElementById('mypass');
            var btn = document.getElementById('myok');
            var links = document.getElementsByTagName('a');
            for(var i=0; i<links.length; i++) {{
                if(links[i].innerText.includes('Account')) {{
                    links[i].click();
                    break;
                }}
            }}
            setTimeout(() => {{
                if(usen && pasd) {{
                    usen.value = '{u}';
                    pasd.value = '{p}';
                    if(btn) btn.click();
                }}
            }}, 1500);
        }})();
        """
        self.browser_view.page().runJavaScript(js)
        self.log("⏳ Running login handshake protocol...")
        QTimer.singleShot(10000, self.check_ready)

    def check_ready(self): 
        self.browser_view.page().runJavaScript("document.getElementById('pct_balance').value", self.verify_login)

    def verify_login(self, val):
        if not val or str(val) == "null":
            # If we fail, wait and retry login sequence instead of bricking completely
            QTimer.singleShot(5000, self.check_ready)
            return

        try:
            balance = float(str(val).strip())
        except Exception as e:
            QTimer.singleShot(5000, self.check_ready)
            return
   
        self.log(f"✅ Active Balance Confirmed: {balance:.8f}")
        self.setup_state(balance)
        self.toggle_engine()

    def deploy_dom_observer(self, success=True):
        # Automatically triggered by the web-frame layout manager anytime a page finishes rendering
        if not success:
            return

        qrc_file = QFile(":/qtwebchannel/qwebchannel.js")
        if qrc_file.open(QIODevice.ReadOnly):
            qwebchannel_source_code = bytes(qrc_file.readAll()).decode("utf-8")
            qrc_file.close()
        else:
            qwebchannel_source_code = ""

        observer_javascript = qwebchannel_source_code + """
        (function() {
            if (window.__diceBotInstalled) return;
            window.__diceBotInstalled = true;

            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.pyBridge = channel.objects.pyBridge;
                let lastBalance = null;
                let lastWins = null;
                let lastLosses = null;

                function tick() {
                    let balanceEl = document.getElementById('pct_balance');
                    let winsEl = document.getElementById('wins');
                    let lossesEl = document.getElementById('losses');

                    if (!balanceEl) return;

                    let balance = balanceEl.value;
                    let wins = winsEl ? winsEl.innerText.replaceAll(',', '') : "0";
                    let losses = lossesEl ? lossesEl.innerText.replaceAll(',', '') : "0";

                    if (balance !== lastBalance || wins !== lastWins || losses !== lastLosses) {
                        lastBalance = balance;
                        lastWins = wins;
                        lastLosses = losses;

                        window.pyBridge.transmit_data(JSON.stringify({
                            balance: balance,
                            wins: wins,
                            losses: losses
                        }));
                    }
                }
                setInterval(tick, 100);
            });
        })();
        """
        self.browser_view.page().runJavaScript(observer_javascript)

    def clean_and_parse_float(self, raw_text):
        if raw_text is None or str(raw_text) == "null" or str(raw_text).strip() == "":
            return 0.0
        try:
            return float(str(raw_text).strip())
        except:
            return 0.0

    def evaluate_financial_sync(self, json_string):
        scraped_data = json.loads(json_string)
        current_wins = self.clean_and_parse_float(scraped_data.get('wins'))
        current_losses = self.clean_and_parse_float(scraped_data.get('losses'))
        current_balance = self.clean_and_parse_float(scraped_data.get('balance'))

        if self.prev_balance is None:
            self.prev_balance = current_balance
            self.last_balance = current_balance
            self.prev_wins = current_wins
            self.prev_losses = current_losses
            return

        if (current_wins == 0 and current_losses == 0) and (self.prev_wins > 0 or self.prev_losses > 0):
            self.log("ℹ️ Site statistics cleared. Wiping tracking memory baseline...")
            self.prev_balance = None
            return

        if current_balance != self.prev_balance: 
            delta = current_balance - self.prev_balance
            
            self.tracked_balance = round(self.tracked_balance + delta, 8)
            self.last_balance = current_balance
            
            # FIXED: Only run anomaly protection if the engine loop is running and active
            if self.is_running and (self.prev_wins > 0 or self.prev_losses > 0):
                if current_losses > self.prev_losses and delta > 0:
                    self.log("🚨 CRITICAL ANOMALY: Balance went UP on match REDS.")
                    sys.exit()
                elif current_wins > self.prev_wins and delta < 0:
                    self.log("🚨 CRITICAL ANOMALY: Balance went DOWN on match GREENS.")
                    sys.exit()

            if current_losses > self.prev_losses:
                self.log(f"⚡ Loss Confirmed: Balance at {current_balance:.8f} | D: {delta:+.8f}")
            elif current_wins > self.prev_wins:
                self.log(f"⚡ Win Confirmed: Balance increased to {current_balance:.8f} | D: {delta:+.8f}")
            
            self.bet_in_flight = False
            self.last_activity_time = time.time()

        self.prev_wins = current_wins
        self.prev_losses = current_losses
        self.prev_balance = current_balance

    def save_state(self):
        try:
            data = {
                "cat": self.cat, "tabby": self.tabby, "felix": self.felix, "orgy": self.orgy, "fart": self.fart,
                "tracked_balance": self.tracked_balance, "initial_balance": self.initial_balance,
                "last_balance": self.last_balance, "next_compound": self.next_compound, 
                "uppers": self.uppers, "downers": self.downers
            }
            with open(STATE_FILE, "w") as f:
                json.dump(data, f)
        except: 
            pass

    def calculate_units(self, balance):
        self.state_data = self.load_state_file()
        if balance == 0: return
        if self.state_data:
            self.tabby = self.state_data.get("tabby")
        else:
            self.tabby = round(balance / 144000, 8)
        
        self.tens = self.tabby * 10.0
        self.sevens = self.tabby * 6.9
        self.eights = self.tabby * 7.9
        self.uppers = 6.9
        self.downers = 2.9

    def setup_state(self, real_bal):
        self.calculate_units(real_bal)
        self.state_data = self.load_state_file()
        
        if self.state_data:
            self.log("📂 Resuming tracking matrices from cache registry...")
            self.cat = self.state_data.get("cat", self.tabby)
            self.fart = int(self.state_data.get("fart", 1))
            self.initial_balance = self.state_data.get("initial_balance", real_bal)
            last_saved = self.state_data.get("last_balance", real_bal)
            drift = real_bal - last_saved
            self.tracked_balance = round(self.state_data.get("tracked_balance", real_bal) + drift, 8)
            self.next_compound = self.state_data.get("next_compound", self.tracked_balance * 1.24)
            self.shadow = 0.0
            
            self.mighty = math.floor(round(self.tracked_balance / self.tens, 8)) * self.tens
            self.felix = self.state_data.get("felix", self.mighty)
            self.orgy = self.state_data.get("orgy", self.mighty)
            self.log(f"⚖️ Deviation Corrected: {drift:.8f}")
        else:
            self.log("🆕 Zero-baseline initialization execution...")
            self.cat = self.tabby
            self.fart = 1
            self.shadow = 0.0
            self.tracked_balance = self.initial_balance = real_bal
            
            self.mighty = math.floor(round(self.tracked_balance / self.tens, 8)) * self.tens
            self.next_compound = self.tracked_balance * 1.24
            self.felix = self.orgy = self.mighty
        
        self.last_balance = real_bal
        self.update_ui_stats()
  
    def load_state_file(self):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                keys = ["cat", "tabby", "felix", "orgy", "tracked_balance", "initial_balance", "last_balance", "next_compound", "uppers", "downers"]
                for k in keys:
                    if k in data: data[k] = float(data[k])
                return data
        except: 
            return None

    def toggle_engine(self):
        self.is_running = True
        self.log(f"🚀 ENGINE ONLINE. Operational Unit: {self.cat:.8f}")
        
        self.last_change_time = time.time()
        self.last_activity_time = time.time()
        self.heartbeat = True
        self.bet_in_flight = False  
        
        # Fire structural action loop
        self.engine_timer.start(150)

    def lol_poop(self):
        self.log("🚨 Websocket stall caught! Re-establishing clean browser runtime context...")
        self.engine_timer.stop()
        self.bet_in_flight = False
        
        self.prev_balance = None
        self.prev_wins = None
        self.prev_losses = None
        
        # Reloading updates DOM and automatically calls deploy_dom_observer because of loadFinished hook
        self.browser_view.reload()
        QTimer.singleShot(15000, self.devils_pooped)
    
    def devils_pooped(self):
        self.kjool_look()

    def process_tick(self):
        if not self.heartbeat or not self.is_running:
            return

        if time.time() - self.last_activity_time > 45:
            self.last_activity_time = time.time()
            self.lol_poop()
            return

        if self.bet_in_flight:
            return

        self.mighty = math.floor(round(self.tracked_balance / self.tens, 8)) * self.tens
        
        if self.tracked_balance >= (self.orgy + (self.tens*self.fart)):
            self.cat = self.tabby
            self.fart = 1
            self.uppers = 6.9
            self.downers = 2.9
            self.felix = float(self.mighty)
            self.orgy = float(self.mighty)
            
        upper_bound_low = round(self.felix + (self.cat * self.uppers), 8)
        upper_bound_high = round(self.felix + (self.cat * (self.uppers + 1.0)), 8)
            
        if (self.tracked_balance > upper_bound_low) and (self.tracked_balance < upper_bound_high):
             self.cat = round(self.cat * 2.0, 8)
             self.uppers = 4.9
             self.downers = 4.9
             self.felix = float(self.tracked_balance)
             
        lower_bound_high = round(self.felix - (self.cat * self.downers), 8)
        lower_bound_low = round(self.felix - (self.cat * (self.downers + 1.0)), 8)
             
        if (self.tracked_balance < lower_bound_high) and (self.tracked_balance > lower_bound_low):
             self.cat = round(self.cat * 2.0, 8)
             self.uppers = 4.9
             self.downers = 4.9
             self.fart = 0
             self.felix = float(self.tracked_balance)
             
        self.update_ui_stats()
        self.save_state()
        
        self.bet_in_flight = True
        jsfool = f"""
        (function() {{
            var b_min = document.getElementById('b_min');
            var pct_chance = document.getElementById('pct_chance');
            var pct_bet = document.getElementById('pct_bet');
            var a_lo = document.getElementById('a_lo');
            
            if(b_min && pct_chance && pct_bet && a_lo) {{
                b_min.click();
                pct_chance.value = '49.5';
                pct_bet.value = '{self.cat:.8f}';
                a_lo.click();
            }}
        }})();
        """
        self.browser_view.page().runJavaScript(jsfool) 

    def update_ui_stats(self):
        self.lbl_balance.setText(f"Bal: {self.last_balance:.8f}")
        self.lbl_profit.setText(f"Life Profit: {(self.tracked_balance - self.initial_balance):.8f}")
        self.lbl_bet.setText(f"Next Bet: {self.cat:.8f}")
        self.lbl_compound.setText(f"Goal: {self.next_compound:.8f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    bot = BotEngine()
    bot.show()
    sys.exit(app.exec_())
