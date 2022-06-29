import pandas as pd
from glob import glob
from pathlib import Path

import mmdet
import mmcv

from mmcv import Config
cfg = Config.fromfile('/ceph/hpc/home/euerikl/projects/fastighet/models/configs/test_cfg_dump.py')

from mmdet.apis import inference_detector, init_detector
checkpoint = '/ceph/hpc/home/euerikl/projects/fastighet/models/cascade_rcnn_1/latest.pth'
model = init_detector(cfg, checkpoint, device='cuda:0')

imgs = glob('/ceph/hpc/scratch/user/euerikl/data/fastighet/miljonsetet/all_batches/10018814/*.tif')
imgs_chunks = [imgs[x:x+8] for x in range(0, len(imgs), 8)]

print(len(imgs_chunks[-1]))

for img in imgs:
    results = inference_detector(model, img)