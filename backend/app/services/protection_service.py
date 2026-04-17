import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification
from app.services.code_scanner import CodeScannerService

class ThreatHandler(FileSystemEventHandler):
    def __init__(self, scanner: CodeScannerService):
        self.scanner = scanner
        self.last_scanned = {}

    def on_modified(self, event):
        if not event.is_directory and '.git' not in event.src_path:
            print(f"[EVENT] File Modified: {os.path.basename(event.src_path)}")
            self._process(event.src_path)

    def on_created(self, event):
        if not event.is_directory and '.git' not in event.src_path:
            print(f"[EVENT] File Created: {event.src_path}")
            self._process(event.src_path)

    def _process(self, target_path):
        # Scan all common script and configuration extensions
        script_extensions = (
            '.py', '.js', '.sh', '.bat', '.ps1', '.vbs', '.reg', 
            '.php', '.rb', '.pl', '.cmd', '.psm1', '.psd1'
        )
        if target_path.lower().endswith(script_extensions):
            try:
                with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                    scanned_content = f.read()
                
                print(f"[*] Analyzing contents of {os.path.basename(target_path)}...")
                scan_result = self.scanner.scan_code(scanned_content)

                print(f"[!] Scan Result: {scan_result['risk_score']}% threat score")

                if scan_result['risk_score'] >= 25:
                    print(f"[CRITICAL] Threat Detected in {target_path}!")
                    self._notify_threat(target_path, scan_result['risk_score'], scan_result['verdict'])
            except Exception as scan_err:
                print(f"Error scanning {target_path}: {scan_err}")

    def _notify_threat(self, path, score, verdict):
        filename = os.path.basename(path)
        print(f"[!] Sending Windows Notification for {filename}...")
        try:
            notification.notify(
                title="🛡️ ZenShield: Threat Blocked!",
                message=f"Malicious content detected in {filename}\nRisk Score: {score}%\nVerdict: {verdict}",
                app_name="ZenShield AI",
                timeout=10
            )
            print("[✓] Notification sent successfully.")
        except Exception as e:
            print(f"[X] Notification failed: {e}")

class ProtectionService:
    def __init__(self):
        self.scanner = CodeScannerService()
        self.observer = Observer()
        self.is_running = False

    def start_monitoring(self, paths_to_watch):
        if self.is_running:
            return
            
        handler = ThreatHandler(self.scanner)
        for path in paths_to_watch:
            if os.path.exists(path):
                self.observer.schedule(handler, path, recursive=True)
                print(f"[*] ZenShield Real-time Protection active on: {path}")
        
        if not self.observer.is_alive():
            self.observer.start()
            
        self.is_running = True

    def stop_monitoring(self):
        if self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            print("[!] ZenShield Real-time Protection deactivated.")
