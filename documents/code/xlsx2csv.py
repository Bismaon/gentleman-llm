import os, sys, subprocess, re, csv, json
from datetime import date
import logging


logger = logging.getLogger(__name__)

end_of_file_decoration = (
    "Fin du rapport"  # the string that decorate the end of the file
)

nbr_empty_lines_on_top_of_ending_string = 2
nbr_leading_decoration_lines = 8


# This function find the date that the XLSX document was fetch from syncro.
# It looks in the first 'nbr_of_file_decoration' lines to find the regex and
# then extract the date.
def find_request_date(nbr_leading_decoration_lines, csvfile):
    for line in csvfile[: nbr_leading_decoration_lines + 1]:
        if m := re.search(r"(Date\s*:\s*)(\d{4}-\d{2}-\d{2})", line):
            return m[2]
    return False


def xlsx2csv(source_file_path, dest_file_path=None):

    try:
        # verify if the source_file_path exist
        if not os.path.isfile(source_file_path):
            logger.error("The file: " + source_file_path + "\ndoesn't exist")
            sys.exit(1)

        # Transforme the excel.xlsx to .csv
        process_result = subprocess.run(
            ["xlsx2csv", "-d;", source_file_path.strip()],
            capture_output=True,
            text=True,
            shell=False,
        )

        if process_result.returncode != 0:
            logger.error("Failed to run xlsx2csv tool")
            sys.exit(1)

        csvfile = process_result.stdout.split("\n")

    except Exception as e:
        logger.error(f"{str(e)}")
        sys.exit(1)

    index_end_of_file = None
    for i, line in enumerate(csvfile[::-1]):
        if re.search(end_of_file_decoration, line):
            index_end_of_file = i
            break
    if index_end_of_file is None:
        logger.error(f"No end of file found with decoration: {end_of_file_decoration}")
        sys.exit(1)

    index_end_of_file = len(csvfile) - index_end_of_file - 1

    # Find the date the file was requested on syncro
    request_date = find_request_date(nbr_leading_decoration_lines, csvfile)
    # If the date was not found, raise error.
    if not request_date:
        raise Exception("XLSX date was not found in ", source_file_path)
    # cut the leading and ending decoration lines
    csvfile = csvfile[
        nbr_leading_decoration_lines : index_end_of_file
        - nbr_empty_lines_on_top_of_ending_string
    ]

    # ------------ get what semestrer the csv file schedule is from----------

    reader = csv.DictReader(csvfile, delimiter=";")
    all_dates = []
    counter_correct_value = 0
    for row in reader:
        if re.match(r"\d{4}-\d{2}-\d{2}", row["Première date No. Cours"]) and re.match(
            r"\d{4}-\d{2}-\d{2}", row["Dernière date No. Cours"]
        ):
            one = date.fromisoformat(row["Première date No. Cours"])
            two = date.fromisoformat(row["Dernière date No. Cours"])
            all_dates.append(one + (two - one) // 2)  # midpoint date
            counter_correct_value += 1
    all_dates.sort()
    mediane_date = all_dates[len(all_dates) // 2]

    if mediane_date.month in range(1, 5):
        sem = "H"
    elif mediane_date.month in range(5, 9):
        sem = "E"
    elif mediane_date.month in range(9, 13):
        sem = "A"
    else:
        sem = "N"

    if mediane_date.month in [1, 5, 9, 12]:
        logger.warning(
            f"mediane_date found on extrem an month, might be an error {mediane_date} in {source_file_path} with {counter_correct_value} lines"
        )

    sem = sem + str(mediane_date.year)[2:]

    # ------END OF ------ get what semestrer the csv file schedule is from------

    if dest_file_path is not None:

        dest_file_name = (
            "_".join(["schedule", sem, request_date, row["Cheminement"]]) + ".csv"
        )

        dest_file_path = (
            dest_file_path + ("" if dest_file_path[-1] == "/" else "/") + dest_file_name
        )

        with open(dest_file_path, "w", encoding="utf-8") as outfile:
            outfile.write("\n".join(csvfile))

    return csvfile  # is a list of each line
