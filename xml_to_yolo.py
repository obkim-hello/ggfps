import os
import xml.etree.ElementTree as ET

# Settings
IMG_FOLDER = 'data/training'  # Folder containing images and XMLs
CLASSES = ['person']  # List your class names here, in order

# Helper: convert box to YOLO format
def convert_bbox(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

for filename in os.listdir(IMG_FOLDER):
    if not filename.endswith('.xml'):
        continue
    xml_path = os.path.join(IMG_FOLDER, filename)
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    yolo_lines = []
    for obj in root.iter('object'):
        cls = obj.find('name').text
        if cls not in CLASSES:
            continue
        cls_id = CLASSES.index(cls)
        xmlbox = obj.find('bndbox')
        b = [int(xmlbox.find('xmin').text), int(xmlbox.find('xmax').text),
             int(xmlbox.find('ymin').text), int(xmlbox.find('ymax').text)]
        bb = convert_bbox((w, h), b)
        yolo_lines.append(f"{cls_id} {' '.join([str(a) for a in bb])}")
    # Write YOLO txt file
    txt_path = os.path.join(IMG_FOLDER, os.path.splitext(filename)[0] + '.txt')
    with open(txt_path, 'w') as f:
        f.write('\n'.join(yolo_lines))
    print(f"Converted {filename} -> {os.path.basename(txt_path)}") 