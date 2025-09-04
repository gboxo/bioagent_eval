import json
with open('task_variants_expanded.json', 'r') as file:
    data = json.load(file)

all_tasks = list(data.keys())


pdb_variants = [(key,list(val["variants"].values())) for key,val in data.items() if "PDB" in val['data_source'] and "UniProt" not in val["data_source"]]


processed_tasks = []


unique_pdb_ids = []
for name,elem in pdb_variants:
    if isinstance(elem, list):
        for e in elem:
            if isinstance(e,list):
                unique_pdb_ids.extend(e)
            elif isinstance(e, str):
                unique_pdb_ids.append(e)
            elif isinstance(e, dict):
                unique_pdb_ids.append(e["pdb_id"])
            else:
                continue
    processed_tasks.append(name)

unique_pdb_ids = set(unique_pdb_ids)

"""
Missing Files

3B4Z
2G8P
1K60
3B4X
2YAG
"""


uniprot_variants = [(key,list(val["variants"].values())) for key,val in data.items() if "PDB" not in val['data_source'] and "UniProt" in val["data_source"]]


unique_uniprot_ids = []
for name,elem in uniprot_variants:
    if isinstance(elem, list):
        for e in elem:
            if isinstance(e,list):
                unique_uniprot_ids.extend(e)
            elif isinstance(e, str):
                unique_uniprot_ids.append(e)
            else:
                continue
    processed_tasks.append(name)

unique_uniprot_ids = set(unique_uniprot_ids)



unprocessed_tasks = set(all_tasks)-set(processed_tasks)
