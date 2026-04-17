import os
import shutil

def get_storage_path(category: str, filename: str = None) -> str:
    """
    Returns a writeable path. On Vercel, this is in /tmp.
    category: 'data', 'reports', etc.
    filename: optional filename to join.
    """
    is_vercel = os.environ.get('VERCEL') == '1'
    
    if is_vercel:
        base = os.path.join('/tmp', category)
    else:
        # Local development path (relative to project root)
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../", category))
        
    os.makedirs(base, exist_ok=True)
    
    if filename:
        return os.path.join(base, filename)
    return base

def sync_data_to_tmp():
    """
    On Vercel, copy static data files from the read-only build dir to /tmp 
    so the app can "simulate" persistent storage for the session.
    """
    if os.environ.get('VERCEL') != '1':
        return

    source_data = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
    target_data = "/tmp/data"
    
    if os.path.exists(source_data):
        os.makedirs(target_data, exist_ok=True)
        for item in os.listdir(source_data):
            s = os.path.join(source_data, item)
            d = os.path.join(target_data, item)
            if os.path.isfile(s) and not os.path.exists(d):
                shutil.copy2(s, d)
