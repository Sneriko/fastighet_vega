import pickle
import json
import itertools
import os

def write_rec(coco_dict, results_det):
    
    with open('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/recog/rec_file.txt', 'w') as f: 
        for inst, img in zip(coco_dict['images'], results_det):  
            for i, annot in enumerate(img[0]):
                try:
                    x1=str(int(annot[0]))
                    y1=str(int(annot[1]))
                    x2=str(int(annot[2]))
                    y2=str(int(annot[3]))
                    f.write(inst['file_name'] + '|' + x1 + '|' + y1 + '|' + x2 + '|' + y1 + '|' + x2 + '|' + y2 + '|' + x1 + '|' + y2 + '|' + '#' + '\n')
                except:
                    print(inst['file_name'])

def write_jsons(coco_dict, results_det):

    tuples = list(zip(coco_dict['images'], results_det))
    batches = dict()

    for key, group in itertools.groupby(tuples, key=lambda x: x[0]['file_name'].split('/')[0]):
        batches[key] = list(group)

    for key, batch in batches.items():
        json_out = os.path.join('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/json', key + '.json')
        
        with open(json_out, 'w', encoding='utf8') as f:
            batch_dict = dict()
            
            for inst in batch:
                page_name = inst[0]['file_name'].split('/')[1].split('.')[0]
                batch_dict[page_name] = list()
                
                for annot in inst[1][0]:
                    entry = dict()
                    entry['det_prob'] = str(annot[4])
                    batch_dict[page_name].append(entry)

            s = json.dumps(batch_dict, indent = 4, ensure_ascii=False, sort_keys=True)
            f.write(str(s))

def main():

    with open('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/pickle/results_det.pkl', 'rb') as f:
        results_det = pickle.load(f)

    with open('/ceph/hpc/home/euerikl/projects/fastighet/data/pipeline_test_data/coco/coco_for_det.json', 'r') as f:
        coco_dict = json.load(f)

    assert len(results_det) == len(coco_dict['images'])

    write_rec(coco_dict, results_det)
    #write_jsons(coco_dict, results_det)

if __name__ == "__main__":
    main()