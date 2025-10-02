import json
import pandas as pd
from json import loads, dumps
from collections import OrderedDict

df = pd.read_csv("programmes_cheminement_type.csv", dtype=str)

# print(df)


def CreateDict(target_subset, target_value):
    result_dictionnary = dict()
    reverse_result_dictionnary = dict()
    df2 = df.drop_duplicates(
        subset=[target_subset], keep="first", inplace=False, ignore_index=False
    )
    df2 = df2[[target_subset, target_value]]
    for index, row in df2.iterrows():
        result_dictionnary[row[target_subset]] = row[target_value]
        if not row[target_value] in reverse_result_dictionnary:
            reverse_result_dictionnary[row[target_value]] = list()
        reverse_result_dictionnary[row[target_value]].append(row[target_subset])
    result_dictionnary = dict(sorted(result_dictionnary.items()))
    reverse_result_dictionnary = dict(sorted(reverse_result_dictionnary.items()))
    return result_dictionnary, reverse_result_dictionnary


faculties = dict()
faculties, discarded_place_holder = CreateDict(
    "Faculté - Identifiant", "Faculté - Description"
)

# print(faculties)

departments = dict()
departments, discarded_place_holder = CreateDict(
    "Département - Identifiant", "Département - Description"
)

programs = dict()
programs, discarded_place_holder = CreateDict("Identifiant", "Description")

programs_to_departments = dict()
departments_to_programs = dict()
programs_to_departments, departments_to_programs = CreateDict(
    "Identifiant", "Département - Identifiant"
)

departments_to_faculties = dict()
faculties_to_departments = dict()
departments_to_faculties, faculties_to_departments = CreateDict(
    "Département - Identifiant", "Faculté - Identifiant"
)

whole_hierarchy = dict()
for faculty in faculties:
    whole_hierarchy[faculty] = dict()
    whole_hierarchy[faculty]["name"] = faculties[faculty]
    whole_hierarchy[faculty]["departments"] = dict()
    for department in faculties_to_departments[faculty]:
        whole_hierarchy[faculty]["departments"][department] = dict()
        whole_hierarchy[faculty]["departments"][department]["name"] = departments[
            department
        ]
        whole_hierarchy[faculty]["departments"][department]["programs"] = dict()
        for program in departments_to_programs[department]:
            whole_hierarchy[faculty]["departments"][department]["programs"][
                program
            ] = dict()
            whole_hierarchy[faculty]["departments"][department]["programs"][program][
                "name"
            ] = programs[program]
            whole_hierarchy[faculty]["departments"][department]["programs"][program][
                "program structure"
            ] = "TODO"
            whole_hierarchy[faculty]["departments"][department]["programs"][program][
                "orientations"
            ] = dict()


with open("whole_hierarchy.json", "w") as outfile:
    json.dump(whole_hierarchy, outfile, indent=4)


with open("faculties.json", "w", encoding="utf-8") as outfile:  # encoding doesn't work
    json.dump(faculties, outfile, indent=4)

with open("departments.json", "w") as outfile:
    json.dump(departments, outfile, indent=4)

with open("programs.json", "w") as outfile:
    json.dump(programs, outfile, indent=4)

with open("programs_to_departments.json", "w") as outfile:
    json.dump(programs_to_departments, outfile, indent=4)

with open("departments_to_programs.json", "w") as outfile:
    json.dump(departments_to_programs, outfile, indent=4)

with open("departments_to_faculties.json", "w") as outfile:
    json.dump(departments_to_faculties, outfile, indent=4)

with open("faculties_to_departments.json", "w") as outfile:
    json.dump(faculties_to_departments, outfile, indent=4)
