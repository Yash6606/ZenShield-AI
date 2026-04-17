import cv2
import numpy as np
import os
import joblib
from PIL import Image, ImageChops
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import io

data_root = r'C:\Users\SHAH VENIL\OneDrive\Desktop\AMD\data\DocTamper Training'
images_dir = os.path.join(data_root, 'images')
masks_dir = os.path.join(data_root, 'masks')

def perform_ela(image_path, quality=90):
    """Simple ELA logic in memory."""
    # Load original
    original = Image.open(image_path).convert('RGB')
    
    # Save as compressed JPG to memory
    buffer = io.BytesIO()
    original.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    compressed = Image.open(buffer)
    
    # Calculate difference
    diff = ImageChops.difference(original, compressed)
    diff_np = np.array(diff)
    
    # Get stats
    mean_val = np.mean(diff_np)
    max_val = np.max(diff_np)
    std_val = np.std(diff_np)
    
    return [mean_val, max_val, std_val]

def train_forgery_model(max_scan=50000):
    print("Scanning dataset for clean/tampered samples...")
    X_clean = []
    X_tampered = []
    
    all_images = os.listdir(images_dir)
    print(f"Scanning up to {max_scan} images...")
    
    for i, img_name in enumerate(all_images[:max_scan]):
        mask_name = img_name.replace('.jpg', '.png')
        img_path = os.path.join(images_dir, img_name)
        mask_path = os.path.join(masks_dir, mask_name)
        
        if not os.path.exists(mask_path): continue
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None: continue
        
        tamper_ratio = np.sum(mask > 10) / (mask.shape[0] * mask.shape[1])
        features = perform_ela(img_path)
        
        if tamper_ratio < 0.0001:
            X_clean.append(features)
        else:
            if len(X_tampered) < 200: 
                X_tampered.append(features)
                
        if len(X_clean) >= 20:
            print("Found 20 clean samples. Stopping early.")
            break
            
        if (i+1) % 1000 == 0:
            print(f"Scanned {i+1} images. Found {len(X_clean)} clean so far...")

    # Balance
    n_samples = min(len(X_clean), len(X_tampered))
    if n_samples < 5:
        print(f"Not enough clean samples found ({len(X_clean)}). Lowering threshold or scanning more.")
        return

    print(f"Found {len(X_clean)} clean and {len(X_tampered)} tampered. Balancing to {n_samples} each.")
    
    X = np.array(X_clean[:n_samples] + X_tampered[:n_samples])
    y = np.array([0]*n_samples + [1]*n_samples)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    print("--- Forgery Model Performance ---")
    print(classification_report(y_test, preds))
    
    models_dir = r'C:\Users\SHAH VENIL\OneDrive\Desktop\AMD\backend\models'
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(model, os.path.join(models_dir, 'forgery_model.joblib'))
    print(f"Model saved to {os.path.join(models_dir, 'forgery_model.joblib')}")

if __name__ == "__main__":
    train_forgery_model(max_scan=10000)
