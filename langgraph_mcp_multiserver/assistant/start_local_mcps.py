"""
Script to start all server instances from local_mcp_servers
"""
import os
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()

# Path to your server folder
server_dir = os.environ["MCP_LOCAL_SERVER_DIR"]

# List to hold subprocesses
processes = []

try:
    # Start each Python file in the folder
    for filename in os.listdir(server_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(server_dir, filename)
            print(f"Starting server: {filename}")
            proc = subprocess.Popen(["python3", filepath])
            processes.append(proc)

    print("\n✅ All servers started. Press Ctrl+C to stop them.\n")

    # Keep the script running until interrupted
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Stopping all servers...")
    for proc in processes:
        proc.kill()
    print("✅ All servers stopped. Goodbye!")
