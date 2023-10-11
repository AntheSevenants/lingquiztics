import subprocess
import os
import argparse

import lingquiztics.questions
import lingquiztics.tools

#
# Argument parsing
#

parser = argparse.ArgumentParser(description='lingquiztics - make quiz')
parser.add_argument('questions', type=str,
					help='Path to the JSON file containing the questions')
parser.add_argument('beamer_header', type=str,
					help='Path to the Quarto file containing the presentation header')
parser.add_argument('--output_file', type=str, nargs='?', default="presentation.html", help='Filename of the presentation')
args = parser.parse_args()

TEMP_FILENAME = "presentation.qmd"

with open(args.beamer_header, "rt") as reader:
    qmd_content = reader.read()

qmd_content = f"{qmd_content}\n\n"

questions = lingquiztics.questions.load("questions.json")

for quiz_round in questions:
    print(quiz_round)

    questions = questions[quiz_round]

    for revision_round in [ False, True ]:
        if not revision_round and quiz_round.startswith("durante"):
            qmd_content += f"# Please hand in your answers for {quiz_round}!\n\n"
            continue

        # Add rounds section
        if not revision_round:
            qmd_content += f"# {quiz_round}\n\n"
        else:
            qmd_content += f"# {quiz_round} (revision)\n\n"

        for index, question in enumerate(questions):
            qmd_content += lingquiztics.questions.output_question(question, index, revision_round)

        if not revision_round:
            qmd_content += f"# Please hand in your answers for {quiz_round}!\n\n"


with open(TEMP_FILENAME, "wt") as writer:
    writer.write(qmd_content)

subprocess.run(["quarto",
                "render", TEMP_FILENAME,
                "--to", "revealjs",
                "-o", args.output_file])

os.remove(TEMP_FILENAME)