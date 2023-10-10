import json
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
args = parser.parse_args()

with open(args.beamer_header, "rt") as reader:
    qmd_content = reader.read()

qmd_content = f"{qmd_content}\n\n"

questions = lingquiztics.questions.load("questions.json")

for quiz_round in questions:
    print(quiz_round)

    # Add rounds section
    qmd_content += f"# {quiz_round}\n\n"

    questions = questions[quiz_round]

    for revision_round in [ False, True ]:
        for index, question in enumerate(questions):
            qmd_content += lingquiztics.questions.output_question(question, index, revision_round)

with open("presentation.qmd", "wt") as writer:
    writer.write(qmd_content)