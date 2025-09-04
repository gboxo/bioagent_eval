import json

with open("examples/react_demo/task_variants_expanded.json", "r") as file:
    data = json.load(file)

all_tasks = list(data.keys())


unique_programs = set()
for task in all_tasks:
    for program in data[task]["required_programs"]:
        unique_programs.add(program)

print(unique_programs)
