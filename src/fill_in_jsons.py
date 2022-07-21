import pickle
import json
from glob import glob
import itertools
import os
from copy import deepcopy
from pathlib import Path

def write_json(json_out, json_dict):

    with open(json_out, 'w', encoding='utf16') as f:
        s = json.dumps(json_dict, indent = 4, ensure_ascii=False, sort_keys=True)
        f.write(str(s))

def fill_in_blanks(results_det, coco_dict):

    path_to_jsons = '/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/json'

    tuples = list(zip(coco_dict['images'], results_det))
    batches = dict()

    for key, group in itertools.groupby(tuples, key=lambda x: x[0]['file_name'].split('/')[0]):
        batches[key] = list(group)

    for key_batch, batch in batches.items():
        json_p = os.path.join(path_to_jsons, key_batch + '.json')
        
        with open(json_p, 'r', encoding='utf16') as f:
            json_dict = json.load(f)

        for i, inst in enumerate(batch):
            if len(inst[1][0]) == 0:
                page_key = inst[0]['file_name'].split('/')[1].split('.')[0]
                json_dict[page_key] = list()

        json_out = os.path.join('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/json/', key_batch + '.json')
        
        write_json(json_out, json_dict)

def fill_in_flipside(batch_jsons):
    
    for batch_json in batch_jsons:

        batch = Path(batch_json).stem
        #print(batch)

        with open(batch_json, 'r', encoding='utf16') as f:
            json_dict = json.load(f)

        for i, (key, page) in enumerate(json_dict.items()):

            if page == []:
                
                page_number = int(key.split('_')[1])
                previous_page = batch + '_' + (str(page_number - 1)).zfill(8)
                next_page = batch + '_' + (str(page_number + 1)).zfill(8)

                if page_number % 2 == 0:
                    json_dict[key] = deepcopy(json_dict[previous_page])
                    for inst in json_dict[key]:
                        inst['cop_from_flipside'] = True

                else:
                    json_dict[key] = deepcopy(json_dict[next_page])
                    for inst in json_dict[key]:
                        inst['cop_from_flipside'] = True

            else:
                continue

        json_out = os.path.join('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/json/', batch + '.json')
        write_json(json_out, json_dict)

def main():

    with open('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/pickle/results_det.pkl', 'rb') as f:
        results_det = pickle.load(f)

    with open('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/coco/coco_for_det.json', 'r') as f:
        coco_dict = json.load(f)

    fill_in_blanks(results_det, coco_dict)

    batch_jsons = glob('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/json/**/*.json', recursive=True)

    fill_in_flipside(batch_jsons)

if __name__ == "__main__":
    main()