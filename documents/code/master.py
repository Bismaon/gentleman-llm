import annuaire_parser, repertoire_parser, xlsx2csv, schedule_parser, faculty_parser
import os, logging, json, argparse, bisect, re
from datetime import date as Date
from pprint import pprint

from utils.db import MongoDB

from utils.pattern import Pattern

pattern = Pattern()
logger = logging.getLogger(__name__)


def main(
    root: str,
    import_links_directory: str,
    schedule_raw_directory: str,
    schedule_parsed_directory: str,
    annuaire_raw_directory: str,
    annuaire_parsed_directory: str,
    repertoire_raw_directory: str,
    repertoire_parsed_directory: str,
    hierarchy_path: str,
    debug: bool = False,
):
    """
    Main function to parse the raw data and populate the database.

    Args:
        root (str): Root directory of the project.
        schedule_raw_directory (str): Directory containing the raw schedule data.
        schedule_parsed_directory (str): Directory containing the parsed schedule data.
        annuaire_raw_directory (str): Directory containing the raw annuaire data.
        annuaire_parsed_directory (str): Directory containing the parsed annuaire data.
        repertoire_raw_directory (str): Directory containing the raw repertoire data.
        repertoire_parsed_directory (str): Directory containing the parsed repertoire data.
        hierarchy_path (str): Path to the hierarchy file.
        debug (bool, optional): Set the logging level to debug. Defaults to False.
    """

    # add root to the directories in order to have the full path if root is given
    schedule_raw_directory = os.path.join(root, schedule_raw_directory)
    schedule_parsed_directory = os.path.join(root, schedule_parsed_directory)

    annuaire_raw_directory = os.path.join(root, annuaire_raw_directory)
    annuaire_parsed_directory = os.path.join(root, annuaire_parsed_directory)

    repertoire_raw_directory = os.path.join(root, repertoire_raw_directory)
    repertoire_parsed_directory = os.path.join(root, repertoire_parsed_directory)
    hierarchy_path = os.path.join(root, hierarchy_path)
    import_links_directory = os.path.join(root, import_links_directory)

    # transform .csv into xlsx
    list_schedules_xlsx = [
        os.path.join(schedule_raw_directory, file)
        for file in os.listdir(schedule_raw_directory)
        if file.rsplit(".")[-1] == "xlsx"
    ]

    # erase the allready present schedule_parsed ( the .csv that came from xlsx2csv )
    for file_path in os.listdir(schedule_parsed_directory):
        if file_path.rsplit(".")[-1] == "csv":
            os.remove(os.path.join(schedule_parsed_directory, file_path))

    for file_path in list_schedules_xlsx:
        file_path = file_path
        xlsx2csv.xlsx2csv(file_path, schedule_parsed_directory)

    # get the list of the raw file to be parsed
    list_schedule = [
        os.path.join(schedule_parsed_directory, file)
        for file in os.listdir(schedule_parsed_directory)
        if file.rsplit(".", 1)[-1] == "csv"
    ]

    list_repertoire = [
        os.path.join(repertoire_raw_directory, file)
        for file in os.listdir(repertoire_raw_directory)
        if file.rsplit(".", 1)[-1] == "pdf"
    ]

    list_annuaire = [
        os.path.join(annuaire_raw_directory, file)
        for file in os.listdir(annuaire_raw_directory)
        if file.rsplit(".", 1)[-1] == "txt"
    ]

    for list_of_file in [list_annuaire, list_repertoire, list_schedule]:
        if len(list_of_file) == 0:
            logger.error(f"The {list_of_file} is empty, script is terminated.")
            exit(1)

    # ----- launch the parsers----
    # --- annuaire
    annuaire = list()
    for file in list_annuaire:
        annuaire += annuaire_parser.parse(file)

    # --- schedule
    # here we are parsing all the files, then sorting them by their fetching date.
    # This way when we combine them in the same dictionnary,  the most recent courses update/overwrite the old ones.
    # For exemple, A24IFT1005 fetched the 2024-7-20 will overwrite A24IFT1005 fetched the 2024-7-15
    schedule_dict_list = []
    schedule_dict = dict()
    for file in list_schedule:
        schedule_dict_list.append(schedule_parser.parse(file))
        # return form is tuple ( date, master_data )
    schedule_dict_list.sort(key=lambda x: x[0])  # sort by date
    for _, dicti in schedule_dict_list:
        schedule_dict.update(dicti)
    for course in schedule_dict.values():
        course["semester_int"] = pattern.semester2int(course["semester"])

    schedule_set = {value["sigle"] for value in schedule_dict.values()}

    # --- repertoire
    repertoire = list()
    for file in list_repertoire:
        repertoire += repertoire_parser.parse(file)

    repertoire_dict = {course["_id"]: course for course in repertoire}
    del repertoire
    repertoire_set = {course_id for course_id in repertoire_dict.keys()}

    # --- faculties
    with open(hierarchy_path, "r", encoding="utf-8") as f:
        faculties = faculty_parser.parse(hierarchy_path)

    faculties = refactor_faculties(
        faculties, {"03": annuaire}, [("v1", import_links_directory)]
    )

    logger.info(f"nbr de facultés dans faculties after refactoring = {len(faculties)}")
    logger.info(f"nbr d'item schedules = {len(schedule_set)}")
    logger.info(f"nbr d'item annuaire = {len(annuaire)}")
    logger.info(f"nbr d'item repertoire = {len(repertoire_set)}")

    # --- merge the data together to be data_model conform ---#

    # Extract courses detail from annuaire and replace those details with a id list
    annuaire_courses_dict = dict()
    for program in annuaire:
        program_courses = list()
        for segment in program["segments"]:
            for bloc in segment["blocs"]:
                bloc_courses = list()
                for course in bloc["courses"]:
                    program_courses.append(course["_id"])
                    bloc_courses.append(course["_id"])
                    annuaire_courses_dict[course["_id"]] = course
                bloc["courses"] = bloc_courses
        program["courses"] = program_courses
    annuaire_courses_set = {course_id for course_id in annuaire_courses_dict.keys()}

    master_data = repertoire_dict
    default_course = lambda course: {
        "_id": course["_id"],
        "name": course["name"] if "name" in course else "",
        "code": course["_id"][:3],
        "number": course["_id"][3:],
        "description": course["description"] if "description" in course else "",
        "credits": course["credit"] if "credit" in course else 0,
        "available_terms": (
            course["available_terms"]
            if "available_terms" in course
            else {"autumn": False, "winter": False, "summer": False}
        ),
        "available_periods": (
            course["available_periods"]
            if "available_periods" in course
            else {"daytime": False, "evening": False}
        ),
        "requirement_text": (
            course["requirement_text"] if "requirement_text" in course else ""
        ),
        "prerequisites_courses": (
            course["prerequisites_courses"] if "prerequisites_courses" in course else []
        ),
        "concomitant_courses": (
            course["concomitant_courses"] if "concomitant_courses" in course else []
        ),
        "equivalent_courses": (
            course["equivalent_courses"] if "equivalent_courses" in course else []
        ),
    }

    # merge schedule
    for course_id in schedule_dict:
        course_id_sch = course_id
        course_id = course_id[3:]
        if course_id not in master_data:
            if course_id in annuaire_courses_set:
                course = default_course(annuaire_courses_dict[course_id])
            else:
                course = default_course(
                    {"_id": course_id, "name": schedule_dict[course_id_sch]["name"]}
                )
            master_data[course_id] = course

    # merge annuaire
    only_annuaire = annuaire_courses_set.difference(schedule_set, repertoire_set)
    for course_id in only_annuaire:
        course = default_course(annuaire_courses_dict[course_id])
        master_data[course_id] = course

    # if no availability in repertoire, take the one from annuaire
    for course_id in repertoire_set.intersection(annuaire_courses_set):
        course = master_data[course_id]
        for key in ["available_terms", "available_periods"]:
            if not any(course[key]):
                course[key] = annuaire_courses_dict[course_id][key]

    db = MongoDB(
        uri=os.getenv("MONGO_URL", "mongodb://localhost:27017"),
        db_name=os.getenv("MONGO_DB_NAME", "planificateur-academique"),
        collection_name=os.getenv("MONGO_COLLECTION_NAME", "courses"),
        logger=logging.getLogger(__name__),
    )
    store_data(master_data, annuaire, faculties, schedule_dict, db)

    schedule_diff = schedule_set.difference(repertoire_set)
    annuaire_diff = annuaire_courses_set.difference(repertoire_set)

    log_insertion_details(
        schedule_diff,
        annuaire_diff,
    )


def store_data(master_data, annuaire, faculties, schedule_dict, db):
    """
    Store the data in the database.

    Args:
        master_data (dict): Dictionary containing the course details.
        annuaire (list): List of annuaire data.
        db (MongoDB): MongoDB object for database connection.
    """
    db.drop()
    db.insert_many([course_detail for course_detail in master_data.values()])

    db.set_collection("programs")
    db.drop()
    db.insert_many(annuaire)

    db.set_collection("faculties")
    db.drop()
    db.insert_many(faculties)

    schedules = [detail for detail in schedule_dict.values()]
    db.set_collection("schedules")
    db.drop()
    db.insert_many(schedules)


def log_insertion_details(
    schedule_diff,
    annuaire_diff,
):
    """
    Log insertion details.

    Args:
        schedule_diff, the difference of schedule set with repertoire set
        annuaire_diff, the difference of annuaire set with repertoire set
    """

    logger.info(
        f"Courses that exist in schedule, but not in repertoire:\n {schedule_diff}\n"
    )
    logger.info(
        f"Courses that exist in annuaire, but not in repertoire:\n {annuaire_diff}\n"
    )
    logger.info(
        f"Courses that exist in annuaire and schedule, but not in repertoire:\n {annuaire_diff.intersection(schedule_diff)}\n"
    )


def find_in_sorted_list(elem, sorted_list):
    "Locate the leftmost value exactly equal to x"
    i = bisect.bisect_left(sorted_list, elem, key=lambda program: program["_id"])
    if i != len(sorted_list) and sorted_list[i]["_id"] == elem:
        return i
    return -1


def refactor_faculties(faculties, annuaires, directories_tuples: list[tuple]):
    """
    annuaire**s** of this form, dict : {  <faculty_id> : <annuaire_object> , ...  }
    """

    faculty2programs = dict()
    for _id, annuaire in annuaires.items():
        annuaire.sort(key=lambda faculty: faculty["_id"])
        faculty2programs[_id] = {program["_id"] for program in annuaire}

    new_faculties = dict()
    links = readImportLinks(directories_tuples)
    for faculty in faculties:
        id_f = faculty["_id"]
        name_f = faculty["name"]
        if id_f in annuaires:
            corresponding_annuaire = annuaires[id_f]
        else:
            continue
        hit_programs = set()
        default_program = lambda x: {
            "_id": x[0],
            "name": x[1],
            "orientation": links[x[0]] if x[0] in links else [],
        }
        for department in faculty["departments"]:
            id_d = department["_id"]
            name_d = department["name"]
            for program in department["programs"]:
                id_p = program["_id"]
                name_p = program["name"]
                if (i := find_in_sorted_list(id_p, corresponding_annuaire)) != -1:
                    hit_programs.add(id_p)
                    name_pa = corresponding_annuaire[i]["name"]
                    new_faculties.setdefault(
                        id_f, {"_id": id_f, "name": name_f, "departments": dict()}
                    )["departments"].setdefault(
                        id_d, {"_id": id_d, "name": name_d, "programs": list()}
                    )[
                        "programs"
                    ].append(
                        default_program((id_p, name_pa))
                    )  # We prefer the name from the annuaire
        program_not_integrated = faculty2programs[id_f].difference(hit_programs)
        autres_dep_list = new_faculties.setdefault(
            id_f, {"_id": id_f, "name": name_f, "departments": dict()}
        )["departments"].setdefault(
            "9999", {"_id": "9999", "name": "Autres", "programs": list()}
        )[
            "programs"
        ]

        for _id in program_not_integrated:
            i = find_in_sorted_list(_id, corresponding_annuaire)
            name = corresponding_annuaire[i]["name"]
            autres_dep_list.append(default_program((_id, name)))
    # transform back to json compliant structure, we need to transform dict into list
    new_faculties = [faculty for faculty in new_faculties.values()]

    for faculty in new_faculties:
        faculty["departments"] = [
            department for department in faculty["departments"].values()
        ]

    return new_faculties


"""
There is many version, because we might change the format of the export
when/if we want to add features, season specification. With version match case,
we can modified the links according to its version so it is standarize.
return a dict  : { program_id : [ URL_link, ... ] }
"""


def readImportLinks(directories_tuples):
    all_links = {}
    for version, directory in directories_tuples:

        files = [os.path.join(directory, file) for file in os.listdir(directory)]

        match version:

            case "v1":
                for file in files:
                    with open(file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for line in lines:
                        program_id = line.split("/")[-4]
                        if not re.match(
                            pattern.program_id_pattern.replace("-", ""), program_id
                        ):
                            logger.error(
                                f"Program id '{program_id}' doesn't match the pattern in file '{file}' of directoy '{directory}'"
                            )
                            continue
                        all_links.setdefault(program_id, list()).append(line.strip())
            case _:
                pass

    return all_links


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse the raw data and populate the database"
    )
    parser.add_argument(
        "--root",
        type=str,
        help="Root directory of the project",
        default=os.path.join("..", ""),
    )
    parser.add_argument(
        "--import-links-directory",
        type=str,
        help="Links used for orientation",
        default=os.path.join("data", "orientation", "v1"),
    )
    parser.add_argument(
        "--schedule-raw-directory",
        type=str,
        help="Directory containing the raw schedule data",
        default=os.path.join("data", "raw", "schedules"),
    )
    parser.add_argument(
        "--schedule-parsed-directory",
        type=str,
        help="Directory containing the parsed schedule data",
        default=os.path.join("data", "parsed", "schedules"),
    )
    parser.add_argument(
        "--annuaire-raw-directory",
        type=str,
        help="Directory containing the raw annuaire data",
        default=os.path.join("data", "raw", "annuaires"),
    )
    parser.add_argument(
        "--annuaire-parsed-directory",
        type=str,
        help="Directory containing the parsed annuaire data",
        default=os.path.join("data", "parsed", "annuaires"),
    )
    parser.add_argument(
        "--repertoire-raw-directory",
        type=str,
        help="Directory containing the raw repertoire data",
        default=os.path.join("data", "raw", "repertoires"),
    )
    parser.add_argument(
        "--repertoire-parsed-directory",
        type=str,
        help="Directory containing the parsed repertoire data",
        default=os.path.join("data", "parsed", "repertoires"),
    )
    parser.add_argument(
        "--hierarchy-path",
        type=str,
        help="Path to the hierarchy file",
        default=os.path.join("data", "faculty", "faculty.csv"),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Set the logging level to debug",
        default=False,
    )

    args = parser.parse_args()
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main(
        args.root,
        args.import_links_directory,
        args.schedule_raw_directory,
        args.schedule_parsed_directory,
        args.annuaire_raw_directory,
        args.annuaire_parsed_directory,
        args.repertoire_raw_directory,
        args.repertoire_parsed_directory,
        args.hierarchy_path,
        args.debug,
    )
