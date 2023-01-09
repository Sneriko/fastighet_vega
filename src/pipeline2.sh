NGPUS=$1
load_path=$2
output_path=$3

#conda activate open-mmlab
 
python batches_to_coco.py $load_path $output_path

echo running detection...

/ceph/hpc/home/euerikl/projects/fastighet/mmdetection/tools/dist_test.sh \
    /ceph/hpc/home/euerikl/projects/fastighet/models/configs/property_cascade_rcnn.py \
    /ceph/hpc/home/euerikl/projects/fastighet/models/checkpoints/cascade_rcnn_1/latest.pth \
    $NGPUS \
    --out $output_path/pickle/results_det.pkl

echo creating recognition_list

python det_res_to_rec.py $output_path

echo running recognition...

/ceph/hpc/home/euerikl/projects/fastighet/mmocr/tools/dist_test.sh \
    /ceph/hpc/home/euerikl/projects/fastighet/models/configs/satrn_plus_test_online_crop.py \
    /ceph/hpc/home/euerikl/projects/fastighet/models/checkpoints/satrn_htr_million_plus_h64/latest.pth \
    $NGPUS \
    --out $output_path/pickle/results_rec.pkl

echo writing jsons...

python rec_to_jsons.py $output_path

echo completing jsons...

python fill_in_jsons.py $output_path
