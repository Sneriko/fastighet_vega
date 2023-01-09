import pickle
import json
import pandas as pd
import itertools
import os
import sys


def flatten_res_det(result_dict_det):
    
    flat_res_det = list()

    for inst in result_dict_det:
        for annot in inst[0]:
            flat_res_det.append(annot[4])

    return flat_res_det

def create_comb_list(rec_list, result_dict_rec, flat_res_det):

    comb_dict_list = list()

    for name, res, det_prob in zip(rec_list, result_dict_rec, flat_res_det):
        
        sub = 0.0
        
        for sc in res['score']:
            sub += 0.27 - (10 * sc)
        
        score = 1.0-sub
        
        comb_dict_list.append({'name': name, 'pred': res['text'], 'pred_conf': str(score), 'det_prob': str(det_prob)})

    return comb_dict_list


def write_jsons(comb_dict_list, output_path):
    
    batches = dict()

    for key, group in itertools.groupby(comb_dict_list, key=lambda x: x['name'].split('/')[0]):
        batches[key] = list(group)

    print(len(batches))

    for key_batch, batch in batches.items():

        json_out = os.path.join(output_path, 'json', key_batch + '.json')
        with open(json_out, 'w', encoding='utf16') as f:

            json_dict = dict()

            for key_page, group in itertools.groupby(batch, key=lambda x: x['name']):
                page_dict = list(group)

                for json_inst in page_dict:
                    json_inst.pop('name', None)

                json_dict[key_page.split('/')[1].split('.')[0]] = page_dict

            s = json.dumps(json_dict, indent = 4, ensure_ascii=False, sort_keys=True)
            f.write(str(s))

def main(argv):

    output_path = argv[0]

    with open(os.path.join(output_path, 'pickle', 'results_rec.pkl'), 'rb') as f:
        result_dict_rec = pickle.load(f)

    with open(os.path.join(output_path, 'pickle', 'results_det.pkl'), 'rb') as f:
        result_dict_det = pickle.load(f)

    rec_df = pd.read_csv(os.path.join(output_path, 'recog', 'rec_file.txt'), delimiter='|', usecols=[0], names=['file_name'])
    rec_list = rec_df['file_name'].tolist()

    flat_res_det = flatten_res_det(result_dict_det)

    comb_dict_list = create_comb_list(rec_list, result_dict_rec, flat_res_det)

    write_jsons(comb_dict_list, output_path)

if __name__ == "__main__":
    main(sys.argv[1:])



