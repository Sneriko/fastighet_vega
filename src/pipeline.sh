NGPUS=$1
 
echo creating coco_file...
 
/ceph/hpc/home/euerikl/.conda/envs/open-mmlab/bin/python /ceph/hpc/home/euerikl/projects/fastighet/src/batches_to_coco.py

echo running detection...

/ceph/hpc/home/euerikl/projects/fastighet/mmdetection/tools/dist_test.sh \
    /ceph/hpc/home/euerikl/projects/fastighet/models/configs/test_cfg_dump.py \
    /ceph/hpc/home/euerikl/projects/fastighet/models/cascade_rcnn_1/latest.pth \
    $NGPUS \
    --out /ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/pickle/results_det.pkl

echo creating recognition_list, writing jsons...

/ceph/hpc/home/euerikl/.conda/envs/open-mmlab/bin/python /ceph/hpc/home/euerikl/projects/fastighet/src/det_res_to_rec.py

echo running recognition...

/ceph/hpc/home/euerikl/projects/fastighet/mmocr/tools/dist_test.sh \
    /ceph/hpc/home/euerikl/projects/fastighet/models/configs/satrn_plus_test_online_crop.py \
    /ceph/hpc/home/euerikl/projects/fastighet/models/satrn_htr_million_plus_h64/latest.pth \
    $NGPUS \
    --out /ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/pickle/results_rec.pkl

echo writing jsons...

/ceph/hpc/home/euerikl/.conda/envs/open-mmlab/bin/python /ceph/hpc/home/euerikl/projects/fastighet/src/rec_to_jsons.py

echo completing jsons...

/ceph/hpc/home/euerikl/.conda/envs/open-mmlab/bin/python /ceph/hpc/home/euerikl/projects/fastighet/src/fill_in_jsons.py