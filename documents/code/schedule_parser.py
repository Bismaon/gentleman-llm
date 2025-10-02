import csv, argparse, logging, os
from pprint import pprint
from datetime import date

# -------------- todo

"""
change again the naming convention of xlsx2csv to only take semester and maybe forget the code 8XXXX
"""


def parse(file_path: str, destination_path=None):
    print(f"Parsing {file_path}")
    semester = file_path.split("_")[1]
    file_date = date.fromisoformat(file_path.split("_")[2].rsplit(".", 1)[0])
    if file_path[0] != "/":
        file_path = os.path.join(os.getcwd(), file_path)
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        master_data = main(semester, reader, file_date)

    if destination_path is not None:
        pass

    return (file_date, master_data)


def main(semester, reader, file_date):

    master_data = dict()

    for row in reader:
        faculty_id = row["Faculté"]
        faculty_name = row["Faculté DL"]
        department_id = row["Comp. Univ."]
        department_name = row["Comp DL"]
        cycle = row["Cheminement"]

        code = row["Mat."]
        number = row["Num. rép."]
        sigle = (code + number).upper()
        section = row["Sect."]
        volet = row["Volet"]
        name = row["Titre"]
        capacity = row["Inscr. Max"]
        number_inscription = row["Inscr."]
        teachers = [
            teacher.strip()
            for teacher in [
                row["Nom enseignant 1"]
                + row["Nom enseignant 2"]
                + row["Nom enseignant 3"]
            ]
            if teacher.strip() != ""
        ]

        mode = row["Mode"]
        statut = row["Statut"]

        days = row["Jour"].split()
        start_time = row["De"]
        end_time = row["A"]
        start_date = row["Du"]
        end_date = row["Au"]

        campus = row["Campus"]
        place = row["Emplacement"]
        pavillon_id = row["Imm."]
        pavillon_name = row["Imm DL"]
        room = row["Salle"]

        _id = semester + sigle

        if statut != "Actif":
            continue

        master_data.setdefault(
            _id,
            {
                "_id": _id,
                "sigle": sigle,
                "fetch_date": date.isoformat(file_date),
                "semester": semester,
                "name": name,
                "sections": dict(),
            },
        )["sections"].setdefault(
            section,
            {
                "number_inscription": number_inscription,
                "teachers": teachers,
                "capacity": capacity,
                "volets": dict(),
            },
        )[
            "volets"
        ].setdefault(
            volet,
            {
                "activities": list(),
            },
        )[
            "activities"
        ].append(
            {
                "days": days,
                "start_time": start_time,
                "end_time": end_time,
                "start_date": start_date,
                "end_date": end_date,
                "campus": campus,
                "place": place,
                "pavillon_name": pavillon_name,
                "room": room,
                "mode": mode,
            }
        )
    # now retransforme the structure to be arrays of object
    for course in master_data.values():

        for section_key, section_dict in course["sections"].items():
            new_volet = [
                volet_dict | {"name": volet_key}
                for volet_key, volet_dict in section_dict["volets"].items()
            ]
            course["sections"][section_key] = section_dict | {"volets": new_volet}
        course["sections"] = [
            section_detail | {"name": section_key}
            for section_key, section_detail in course["sections"].items()
        ]

    return master_data


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Parses the schedules")

    argparser.add_argument("--file_path", type=str, default=None)
    argparser.add_argument("--destination_path", type=str, default=None)
    argparser.add_argument("--print_course", type=str, default=None)

    argparser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = argparser.parse_args()

    logger = logging.getLogger(__name__)

    if args.file_path is None:
        logger.error("No source file to parse given")
        exit(1)

    date, data = parse(args.file_path, args.destination_path)
    if not args.debug and args.print_course:
        pprint(data[args.print_course])

    if args.debug:
        if args.print_course:
            pprint(data[args.print_course])
        elif "IFT1015" in data:
            pprint(data["IFT1015"])
        else:
            pprint([elem for elem in data.values()][0])
