import pandas as pd
from glob import glob
from pathlib import Path
import json
import os

import mmdet
import mmcv
import time

from mmcv import Config
from mmdet.apis import inference_detector, init_detector

import torch.distributed as dist
import torch.multiprocessing as mp

def run_inference(rank, world_size):

    cfg = Config.fromfile('/ceph/hpc/home/euerikl/projects/fastighet/models/configs/test_cfg_dump.py')


    checkpoint = '/ceph/hpc/home/euerikl/projects/fastighet/models/cascade_rcnn_1/latest.pth'
    model = init_detector(cfg, checkpoint, device='cuda:0')

    imgs = glob('/ceph/hpc/scratch/user/euerikl/data/fastighet/miljonsetet/all_batches/10018814/*.tif')
    imgs_chunks = [imgs[x:x+8] for x in range(0, len(imgs), 8)]

    output_path = os.path.join('/ceph/hpc/home/euerikl/projects/fastighet/output', '10018814')
    Path(output_path).mkdir(exist_ok=True)

    batch_json = dict()

    t0 = time.time()
    print('start')

    for chunk in imgs_chunks:
        results = inference_detector(model, chunk)
        for i, img_p in enumerate(chunk):
            
            img_name = Path(img_p).stem
            batch_json[img_name] = []

            im = mmcv.imread(img_p)

            for j,bb in enumerate(results[i][0]):

                batch_json[img_name].append(dict())
                batch_json[img_name][j]['det_prob'] = str(bb[4])

                
                file_name = Path(img_p).stem + '_' + str(j).zfill(3) + '.tif'
                file_out = os.path.join(output_path, file_name)

                cropped_img = mmcv.imcrop(im, bb[0:4])
                mmcv.imwrite(cropped_img, file_out)

    t1 = time.time()

    total_time = t1-t0

    print(total_time)

def main():
    world:size = 4
