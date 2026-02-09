#!/usr/bin/env python3
import sys
import time
import random
import socket
import ssl
import urllib.parse
import http.client
from multiprocessing import Process, Manager

# --- Configuration ---
BANNER = """
***************************************************
*                [ LOAD CANNON ]                  *
* * * * * * * * * * * * * * * * * * * * *  * * *  *                                                  
*     L O A D  ::  F I R E  ::  C R A S H         *
* * * * * * * * * * * * * * * * * * * * *  * * *  *
*      Interactive Load Tester (Educational)      *
***************************************************
"""

# =========================
# 1. Advanced User-Agent Generator (Fixed)
# =========================
def generate_user_agents(count=1500, seed=None):
    if seed: random.seed(seed)
    
    # Expanded Version Pools
    chrome_versions = list(range(110, 125))
    firefox_versions = list(range(110, 125))
    safari_versions = ["16.6", "17.0", "17.1", "17.2", "17.3", "17.4", "17.5"]
    edge_versions = list(range(110, 125))
    
    windows_versions = ["10.0", "11.0"]
    macos_versions = ["12_6", "13_6", "14_2", "14_3", "14_4"]
    android_versions = ["11", "12", "13", "14"]
    ios_versions = ["16_6", "17_0", "17_1", "17_2", "17_3", "17_4"]
    
    android_devices = ["Pixel 6", "Pixel 7", "Pixel 8 Pro", "SM-G991B", "SM-G996B", "SM-A515F", "OnePlus 11"]
    
    uas = set()
    attempts = 0
    max_attempts = count * 10 # Safety break
    
    while len(uas) < count and attempts < max_attempts:
        attempts += 1
        platform = random.choice(["windows", "macos", "linux", "android", "ios"])
        
        # Random Build Numbers for Entropy (Fixes infinite loop)
        build_a = random.randint(1000, 9999)
        build_b = random.randint(0, 150)
        
        if platform == "windows":
            win = random.choice(windows_versions)
            browser = random.choice(["chrome", "firefox", "edge"])
            if browser == "chrome":
                v = random.choice(chrome_versions)
                ua = f"Mozilla/5.0 (Windows NT {win}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.{build_a}.{build_b} Safari/537.36"
            elif browser == "edge":
                v = random.choice(edge_versions)
                ua = f"Mozilla/5.0 (Windows NT {win}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.{build_a}.{build_b} Safari/537.36 Edg/{v}.0.{build_a}.{build_b}"
            else:
                v = random.choice(firefox_versions)
                ua = f"Mozilla/5.0 (Windows NT {win}; Win64; x64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
                
        elif platform == "macos":
            mac = random.choice(macos_versions)
            browser = random.choice(["chrome", "firefox", "safari"])
            if browser == "chrome":
                v = random.choice(chrome_versions)
                ua = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.{build_a}.{build_b} Safari/537.36"
            elif browser == "firefox":
                v = random.choice(firefox_versions)
                ua = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac.replace('_', '.')}; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
            else:
                v = random.choice(safari_versions)
                ua = f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{v} Safari/605.1.15"
                
        elif platform == "linux":
            browser = random.choice(["chrome", "firefox"])
            if browser == "chrome":
                v = random.choice(chrome_versions)
                ua = f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.{build_a}.{build_b} Safari/537.36"
            else:
                v = random.choice(firefox_versions)
                ua = f"Mozilla/5.0 (X11; Linux x86_64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
                
        elif platform == "android":
            av = random.choice(android_versions)
            dev = random.choice(android_devices)
            v = random.choice(chrome_versions)
            ua = f"Mozilla/5.0 (Linux; Android {av}; {dev}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.{build_a}.{build_b} Mobile Safari/537.36"
            
        else: # ios
            iv = random.choice(ios_versions)
            sv = random.choice(safari_versions)
            device = random.choice(["iPhone", "iPad"])
            ua = f"Mozilla/5.0 ({device}; CPU {device} OS {iv} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{sv} Mobile/15E148 Safari/604.1"
            
        uas.add(ua)
        
    return list(uas)

# Pre-generate agents to share across processes
print("🔹 Generating 1,500 Unique User-Agents...")
USER_AGENTS = generate_user_agents(1500)
print(f"✅ Done. ({len(USER_AGENTS)} generated)")

# =========================
# 2. Cannon Worker (The Engine)
# =========================
class CannonWorker(Process):
    def __init__(self, target_url, nr_sockets, counter, method):
        super(CannonWorker, self).__init__()
        self.counter = counter
        self.nr_socks = nr_sockets
        self.url = target_url
        self.socks = []
        self.runnable = True
        self.method = method
        
        # URL Parsing
        if not self.url.startswith("http"):
            self.url = "http://" + self.url
            
        parsed = urllib.parse.urlparse(self.url)
        self.ssl = (parsed.scheme == 'https')
        self.host = parsed.netloc.split(':')[0]
        self.path = parsed.path or "/"
        self.port = parsed.port or (443 if self.ssl else 80)

    def build_random_string(self, size):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(chars) for _ in range(size))

    def generate_url(self):
        separator = "&" if "?" in self.path else "?"
        qs = f"t={self.build_random_string(5)}"
        return f"{self.path}{separator}{qs}"

    def run(self):
        while self.runnable:
            try:
                # -----------------------------------
                # A. Refill Socket Pool (Connection)
                # -----------------------------------
                needed = self.nr_socks - len(self.socks)
                if needed > 0:
                    for _ in range(needed):
                        try:
                            if self.ssl:
                                ctx = ssl._create_unverified_context()
                                c = http.client.HTTPSConnection(self.host, self.port, timeout=4, context=ctx)
                            else:
                                c = http.client.HTTPConnection(self.host, self.port, timeout=4)
                            self.socks.append(c)
                        except Exception:
                            break

                # -----------------------------------
                # B. Fire Requests (High Throughput)
                # -----------------------------------
                # We iterate a copy so we can modify the original list safely
                for conn in list(self.socks):
                    try:
                        url = self.generate_url()
                        headers = {
                            'User-Agent': random.choice(USER_AGENTS),
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive', # Key for speed
                            'Host': self.host
                        }
                        
                        req_method = random.choice(['GET', 'POST']) if self.method == 'RANDOM' else self.method
                        
                        # Send Request
                        conn.request(req_method, url, headers=headers)
                        
                        # Read Response
                        resp = conn.getresponse()
                        resp.read() # Consume body to clear buffer
                        
                        self.inc_counter()
                        
                        # Optimization: Close only if server asks to close
                        # Otherwise, keep socket open for next loop (Keep-Alive)
                        if resp.getheader("Connection") == "close":
                            conn.close()
                            if conn in self.socks: self.socks.remove(conn)
                            
                    except (socket.error, http.client.HTTPException):
                        # Socket died or timed out
                        self.inc_failed()
                        if conn in self.socks: self.socks.remove(conn)
                    except Exception:
                        self.inc_failed()
                        if conn in self.socks: self.socks.remove(conn)
                
            except Exception:
                pass # Main loop error handler

    def inc_counter(self):
        try: self.counter[0] += 1
        except: pass

    def inc_failed(self):
        try: self.counter[1] += 1
        except: pass

    def stop(self):
        self.runnable = False

# =========================
# 3. Interactive CLI
# =========================
def get_input(prompt, default=None):
    if default:
        user_in = input(f"🔹 {prompt} [{default}]: ").strip()
        return user_in if user_in else default
    return input(f"🔹 {prompt}: ").strip()

def main():
    print(BANNER)
    print("⚠️  WARNING: Only run this against servers YOU own.")
    print("   Unauthorized stress testing is illegal.\n")
    
    agree = input("Do you have permission to test the target? (y/n): ").lower()
    if agree != 'y':
        print("❌ Aborting.")
        sys.exit(1)
        
    print("\n" + "="*50)
    
    # 1. Target
    target = get_input("Enter Target IP or URL (e.g. 127.0.0.1)")
    if not target:
        print("❌ Target is required.")
        sys.exit(1)

    # 2. Method
    print("\n" + "-"*50)
    print("📡 HTTP METHOD SELECTION")
    print("   1. GET    : Standard request.")
    print("   2. POST   : Submits data (heavier load).")
    print("   3. RANDOM : Mixes GET/POST (chaotic).")
    print("-" * 50)
    
    method_choice = get_input("Select Method (1-3)", "1")
    if method_choice == "2": method = "POST"
    elif method_choice == "3": method = "RANDOM"
    else: method = "GET"

    # 3. Workers
    print("\n" + "-"*50)
    print("👥 WORKERS (Processes)")
    print("   - Low (2-5)    : Debugging")
    print("   - Med (10-20)  : Stress Test")
    print("   - High (50+)   : Extreme Load")
    print("-" * 50)
    try: workers = int(get_input("Number of Workers", "10"))
    except: workers = 10

    # 4. Sockets
    print("\n" + "-"*50)
    print("🔌 SOCKETS (Connections per Worker)")
    print("   - Low (10)     : Light")
    print("   - Med (100)    : Heavy")
    print("   - High (500)   : Maximum")
    print("-" * 50)
    try: sockets = int(get_input("Sockets per Worker", "100"))
    except: sockets = 100

    # Confirmation
    total_conns = workers * sockets
    print("\n" + "="*50)
    print(f"🚀 READY TO FIRE")
    print(f"   🎯 Target:  {target}")
    print(f"   📡 Method:  {method}")
    print(f"   💥 Total:   {total_conns} concurrent connections")
    print("="*50)
    input("Press ENTER to start (CTRL+C to stop)...")

    # Execution
    manager = Manager()
    counter = manager.list([0, 0])
    pool = []

    for i in range(workers):
        try:
            w = CannonWorker(target, sockets, counter, method)
            w.start()
            pool.append(w)
        except Exception as e:
            print(f"❌ Failed to start worker: {e}")

    print("\n🔥 FIRE! (Monitoring started...)")
    start_time = time.time()
    try:
        while True:
            elapsed = time.time() - start_time
            hits = counter[0]
            failed = counter[1]
            rps = hits / elapsed if elapsed > 0 else 0
            
            sys.stdout.write(f"\r🚀 Hits: {hits} | ❌ Failed: {failed} | ⚡ RPS: {rps:.2f}")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
        for w in pool:
            w.terminate()
        print("✅ Done.")

if __name__ == "__main__":
    main()