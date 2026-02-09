# 🚀 LoadCannon
<pre><code>

RedEye

</code></pre>
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-2496ED)
![Platform](https://img.shields.io/badge/platform-linux-critical)
![Status](https://img.shields.io/badge/status-active_defense-red)

High-Concurrency HTTP/S Load Testing Tool Python 3 | Multiprocessing | Socket Pooling

<b>⚠️ DISCLAIMER</b>

FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY. 

This tool generates significant traffic and can cause Denial of Service (DoS) conditions.
 Only run this against servers you own or have explicit written permission to test. 
 
 The author is not responsible for any misuse or damage caused by this program.

📖 Overview
LoadCannon is a modern, interactive stress-testing tool designed to evaluate web server resilience. 

Unlike simple request flooders, LoadCannon uses a Worker + Socket Pool architecture. This allows it to hold open thousands of concurrent connections with minimal CPU usage on the attacking machine, simulating realistic high-traffic events or Layer 7 resource exhaustion attacks.

<b>🔥 Key Features</b>

    Interactive CLI: Guided setup for every test run.

    Multi-Process Architecture: Uses Python's multiprocessing to bypass the GIL (Global Interpreter Lock) for true parallelism.

    Socket Pooling: Maintains persistent Keep-Alive connections to exhaust server file descriptors.

    Traffic Mixing: Supports GET, POST, and RANDOM HTTP methods to test different logic paths.

    Realism: Rotates User-Agents and randomizes query strings to bypass simple caching layers.

    SSL/TLS Support: Natively handles HTTPS connections.

## ⚙️ Installation

No external dependencies are required. LoadCannon runs on standard Python 3 libraries.

    Clone or Download:
<code>git clone https://github.com/krintoxi/RedEye.git

cd RedEye</code>

<b>Run:</b>
<code>python3 RedEye.py</code>

# 🐳 Docker Guide (Recommended)

Running LoadCannon in Docker is the easiest way to ensure a clean environment without version conflicts.

<b>1. Build the Image</b>

Navigate to the folder containing load_cannon.py and Dockerfile.

<code>docker build -t RedEye .</code>

<b>2. Run the Cannon</b>

We use  --network host to bypass Docker's network bridge for maximum performance.

<code>docker run -it --rm --network host RedEye</code>

    --rm: Removes the container after you exit.
    --it: Runs in interactive mode (required for the menu).
    --network host: Allows the container to use your host's full network stack.

#### 🕹️ Usage Guide

LoadCannon is designed to be interactive. Simply run the script and follow the prompts.
<b>1. Target Configuration</b>

You will be asked for the target IP or URL.

    Valid: 127.0.0.1, example.com, https://mysite.com

    Note: If you do not specify a protocol, http:// is assumed.

<b>2. Attack Method</b>

Choose how the cannon fires:

    [1] GET: Standard requests. Good for testing bandwidth and static file serving.

    [2] POST: Sends data payloads. Good for testing database bottlenecks and processing logic.

    [3] RANDOM: Randomly switches between GET and POST. Simulates chaotic real-world traffic.

## 3. Load Tuning

LoadCannon calculates load as:

**Total Connections = Workers × Sockets**

### Settings

| Setting | Description | Recommended |
|-------|------------|-------------|
| **Workers** | Separate CPU processes | 5–10 (Consumer PC), 20+ (Server) |
| **Sockets** | Connections per worker | 50 (Standard), 500+ (Stress Test) |

### Example

- **Workers:** 10  
- **Sockets:** 100  

**Result:** **1,000 concurrent connections**

🧠 Technical Details
Architecture

LoadCannon avoids the overhead of creating a new TCP handshake for every request.

    Initialization: It spawns N independent Worker processes.

    Pool Filling: Each Worker opens M sockets to the target.

    Fire Loop: The Worker iterates through its socket pool, sending HTTP requests over the open connections (Keep-Alive).

    Resurrection: If a socket dies (server closes connection), the Worker immediately creates a new one to maintain the target load.

Defense Verification

Use LoadCannon to test if your server:

    Correctly limits Requests Per Second (RPS).

    Bans IPs that generate excessive 404/403 errors.

    Can handle high concurrency without crashing the database.

🛑 Stopping the Test

To stop the bombardment, simply press CTRL+C in the terminal. The tool will gracefully terminate all worker processes and close sockets.

"With great power comes great responsibility."
