from glob import glob
import mmcv
from pathlib import PurePath
import json
import multiprocessing as mp

def create_inst(img_p):
    
    img_dict = dict()
    
    img = mmcv.imread(img_p)
    
    height = img.shape[0]
    width = img.shape[1]
    file_name = ('/').join(PurePath(img_p).parts[-2:])

    img_dict['width'] = width
    img_dict['height'] = height
    #img_dict['id'] = i
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


def main():

    imgs = glob('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/batches/**/*.tif')
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

    with open('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/coco/coco_for_det.json', 'w', encoding='utf8') as f:
        coco_str = json.dumps(coco, indent = 4, ensure_ascii=False)
        f.write(str(coco_str))

if __name__ == "__main__":
    main()





"""
imgs = glob('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/batches/**/*.tif')
imgs.sort()

coco = dict()

coco['images'] = list()

for i, img_p in enumerate(imgs):
    
    img_dict = dict()
    
    img = mmcv.imread(img_p)
    
    height = img.shape[0]
    width = img.shape[1]
    file_name = ('/').join(PurePath(img_p).parts[-2:])

    img_dict['width'] = width
    img_dict['height'] = height
    img_dict['id'] = i
    img_dict['file_name'] = file_name

    coco['images'].append(img_dict)

coco['categories'] = list()
cat_prop = dict()
cat_prop['id'] = 0
cat_prop['name'] = 'property'
coco['categories'].append(cat_prop)

with open('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/coco/coco_for_det.json', 'w', encoding='utf8') as f:
    coco_str = json.dumps(coco, indent = 4, ensure_ascii=False)
    f.write(str(coco_str))
"""
