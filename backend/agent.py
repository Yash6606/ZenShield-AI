import os
import threading
import uvicorn
import webbrowser
import sys
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from app.services.protection_service import ProtectionService

# Initialize the Protection Service
protection_service = ProtectionService()

def create_tray_icon():
    # Create a simple red/orange shield icon if real one missing
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (10, 12, 16))
    dc = ImageDraw.Draw(image)
    # Draw a shield shape
    dc.polygon([(32, 5), (55, 15), (55, 40), (32, 60), (9, 40), (9, 15)], fill=(234, 88, 12)) 
    return image

def launch_dashboard(icon, item):
    webbrowser.open("http://localhost:5173")

def toggle_protection(icon, item):
    if protection_service.is_running:
        protection_service.stop_monitoring()
    else:
        # Monitor the parent directory (project root) and Downloads
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        protection_service.start_monitoring([project_root, downloads_path])

def exit_action(icon, item):
    protection_service.stop_monitoring()
    icon.stop()
    os._exit(0)

def run_api_server():
    # Import app here to avoid circular imports
    from main import app
    print("[*] Starting Backend API Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def main():
    # 1. Start Backend in background thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()

    # 2. Start Protection in background thread (default ON)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    protection_service.start_monitoring([project_root, downloads_path])

    # 3. Create System Tray Icon
    menu = Menu(
        MenuItem("Open ZenShield Dashboard", launch_dashboard),
        MenuItem("Active Protection", toggle_protection, checked=lambda item: protection_service.is_running),
        Menu.SEPARATOR,
        MenuItem("Exit ZenShield", exit_action)
    )

    icon = Icon("ZenShield AI", create_tray_icon(), "ZenShield AI - Active", menu)
    
    print("[*] ZenShield AI Software Agent is running.")
    print("[*] Access dashboard at http://localhost:5173")
    
    icon.run()

if __name__ == "__main__":
    main()
