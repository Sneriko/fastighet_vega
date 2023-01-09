from glob import glob
import mmcv
from pathlib import PurePath
import json
import multiprocessing as mp
import sys
import os

def create_inst(img_p):
    
    img_dict = dict()
    
    img = mmcv.imread(img_p)
    
    height = img.shape[0]
    width = img.shape[1]
    file_name = ('/').join(PurePath(img_p).parts[-2:])

    img_dict['width'] = width
    img_dict['height'] = height
    img_dict['file_name'] = file_name

    return img_dict

def sort_imgs_add_id(img_list):
    
    img_list = sorted(img_list, key=lambda x: x['file_name'])
    
    for i, inst in enumerate(img_list):
        inst['id'] = i

    return img_list

def add_cat_to_coco(coco):
    
    coco['categories'] = list()
    
    cat_prop = dict()
    cat_prop['id'] = 0
    cat_prop['name'] = 'property'
    
    coco['categories'].append(cat_prop)

    return coco

def main(argv):

    load_path = argv[0]
    output_path = argv[1]

    imgs = glob(os.path.join(load_path, '**', '**'))
    print(len(imgs))
    imgs.sort()

    mp.freeze_support()
    p = mp.Pool()
    img_list = p.map(create_inst, imgs)
    p.close()
    p.join()

    img_list = sort_imgs_add_id(img_list)

    assert len(imgs) == len(img_list)
    
    coco = dict()
    coco['images'] = img_list
    
    coco = add_cat_to_coco(coco)

    with open(os.path.join(output_path , 'coco', 'coco_for_det.json'), 'w', encoding='utf8') as f:
        coco_str = json.dumps(coco, indent = 4, ensure_ascii=False)
        f.write(str(coco_str))

if __name__ == "__main__":
    
    print(sys.argv[1:])
    main(sys.argv[1:])                  