import os
import shutil
import random

def prepare_data(source_dir, output_dir, train_ratio=0.8):
    # Create target directories
    for split in ['train', 'val']:
        os.makedirs(os.path.join(output_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', split), exist_ok=True)

    # Get all image files (assuming common extensions)
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    files = [f for f in os.listdir(source_dir) if f.lower().endswith(image_extensions)]
    random.shuffle(files)

    split_idx = int(len(files) * train_ratio)
    train_files = files[:split_idx]
    val_files = files[split_idx:]

    def copy_files(file_list, split):
        for img_file in file_list:
            base_name = os.path.splitext(img_file)[0]
            lbl_file = base_name + '.txt'
            
            # Source paths
            src_img = os.path.join(source_dir, img_file)
            src_lbl = os.path.join(source_dir, lbl_file)

            # Dest paths
            dst_img = os.path.join(output_dir, 'images', split, img_file)
            dst_lbl = os.path.join(output_dir, 'labels', split, lbl_file)

            if os.path.exists(src_lbl):
                shutil.copy(src_img, dst_img)
                shutil.copy(src_lbl, dst_lbl)

    print(f"Copying {len(train_files)} files to train...")
    copy_files(train_files, 'train')
    print(f"Copying {len(val_files)} files to val...")
    copy_files(val_files, 'val')

    # Create data.yaml
    yaml_content = f"""path: {os.path.abspath(output_dir)}
train: images/train
val: images/val

nc: 1
names: ['person']
"""
    with open(os.path.join(output_dir, 'data.yaml'), 'w') as f:
        f.write(yaml_content)
    print("data.yaml created.")

if __name__ == "__main__":
    prepare_data('thermal_data_new/ALL_IN_ONE_RGB_IMG_ANOT', 'thermal_data_new')
