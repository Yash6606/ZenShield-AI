import cv2
import numpy as np
import os

data_root = r'c:\Users\SHAH VENIL\OneDrive\Desktop\AMD\data'
folder = 'DocTamper Training'

def find_balanced_subset(n=5000):
    images_path = os.path.join(data_root, folder, 'images')
    masks_path = os.path.join(data_root, folder, 'masks')
    
    if not os.path.exists(images_path): return
    
    clean_samples = []
    tampered_samples = []
    
    # Get a listing of files
    all_images = os.listdir(images_path)
    print(f"Total images in folder: {len(all_images)}")
    
    for i, img_name in enumerate(all_images[:n]):
        mask_name = img_name.replace('.jpg', '.png')
        mask_file = os.path.join(masks_path, mask_name)
        
        if not os.path.exists(mask_file): continue
            
        mask = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)
        if mask is None: continue
        
        tamper_ratio = np.sum(mask > 10) / (mask.shape[0] * mask.shape[1])
        if tamper_ratio < 0.0001:
            clean_samples.append(img_name)
        else:
            tampered_samples.append(img_name)
            
        if (i+1) % 1000 == 0:
            print(f"Checked {i+1} samples...")

    print(f"Final Count:")
    print(f"  Clean: {len(clean_samples)}")
    print(f"  Tampered: {len(tampered_samples)}")

if __name__ == "__main__":
    find_balanced_subset(10000)
