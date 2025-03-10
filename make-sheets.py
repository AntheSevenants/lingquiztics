import argparse
import subprocess
import os
import sys
import math

from pathlib import Path

import lingquiztics.questions
import lingquiztics.tools

#
# Argument parsing
#

parser = argparse.ArgumentParser(description='lingquiztics - make answer sheets')
parser.add_argument('questions', type=str,
					help='Path to the JSON file containing the questions')
parser.add_argument('sheets_header', type=str,
					help='Path to the Quarto file containing the answer sheets header')
parser.add_argument('--team_names', type=str, nargs='?', default=None, help='Path to text file with team names (one per line)')
parser.add_argument('--key', type=bool, nargs='?', default=False, help='Whether to print a key sheet')
parser.add_argument('--output_file', type=str, nargs='?', default="answer_sheets.pdf", help='Filename of the answer sheets')
parser.add_argument('--keep_md', type=bool, nargs='?', default=False, help='Whether to keep the Markdown file')
parser.add_argument('--no_chain', type=bool, nargs='?', default=False, help='Whether to chain the output to Quarto immediately')
parser.add_argument('--double_points', type=bool, nargs='?', default=False, help='Whether to give opportunity to double points')
args = parser.parse_args()

TEMP_FILENAME = "answer_sheets.qmd"

no_chain = args.no_chain is not False
double_points = args.double_points is not False

with open(args.sheets_header, "rt") as reader:
    qmd_content = reader.read()

key = args.key is not False

qmd_content = f"{qmd_content}\n\n"

rounds = lingquiztics.questions.load(args.questions)

questions_basedir = Path(args.questions).parent

if not key:
    team_names = [ " " ]
else:
    team_names = [ "key" ]

if args.team_names is not None and not key:
    with open(args.team_names, "rt") as reader:
        team_names = reader.read().split("\n")

for team_name in team_names:
    if double_points:
        qmd_content += lingquiztics.tools.render_header("Double your points!", team_name)

        qmd_content += "\\Large Please select the round for which you want your points to be doubled. \\Huge\n\n"

        qmd_content += "\n".join([ f"1. $\\square$ {round_name}" for round_name in rounds if not round_name.startswith("durante_") and round_name != "Break" ])
        qmd_content += "\n\n \\normalsize"
        qmd_content += "\n\n{{< pagebreak >}}\n\n"

    for round_no, quiz_round in enumerate(rounds):
        print(quiz_round)

        if quiz_round == "Break":
            continue

        questions = rounds[quiz_round]

        durante = quiz_round.startswith("durante_")
        quiz_round = quiz_round.replace("durante_", "")

        qmd_content += lingquiztics.tools.render_header(quiz_round, team_name)

        if "durante":
            if "question_general" in questions[0]:
                general_question = questions[0]["question_general"]
                qmd_content += f"```{{=latex}}\n\\begin{{center}}\n\\large {general_question}\n\\end{{center}}\n```\n"
        
        table_start = "```{=latex}\n\
\\begingroup\n\
\\setlength{\\tabcolsep}{20pt}\n\
\\renewcommand{\\arraystretch}{1.5}\n\
\\begin{tabularx}{\\textwidth}{|>{\\centering\\arraybackslash}X|>{\\centering\\arraybackslash}X|}\n\
\\hline\n"

        table_end = "\\end{tabularx}\n\
\\endgroup\n\
```\n\n"

        if durante:
            # Image round
            if "images" in questions[0]:
                # Header
                qmd_content += table_start
                questions_no = len(questions)
                pair_count = math.ceil(questions_no / 2)
                
                for q_index in range(pair_count):
                    l_index = 2 * q_index + 1
                    r_index = 2 * q_index + 2

                    left_question = questions[l_index - 1]
                    right_question = questions[r_index - 1]

                    left_image = left_question["images"][0]
                    right_image = right_question["images"][0]

                    relative_left_image = os.path.join(questions_basedir, left_image)
                    relative_right_image = os.path.join(questions_basedir, right_image)

                    left_answer = left_question["answer"]
                    right_answer = right_question["answer"]

                    qmd_content += f"\
\\includegraphics[width=0.28\\textwidth]{{{relative_left_image}}} & \\includegraphics[width=0.28\\textwidth]{{{relative_right_image}}}\\\\\n"
                    
                    if not key:
                        qmd_content += f"{l_index}. ..................................................... & {r_index}. ..................................................... \\\\\n\
\\hline\n"
                    else:
                        qmd_content += f"{l_index}.{left_answer} & {r_index}. {right_answer} \\\\\n\
\\hline\n"
                    
                    # if q_index == 2:
                    #      qmd_content += table_end
                    #      qmd_content += "\n\n{{< pagebreak >}}\n\n"
                    #      qmd_content += table_start

                qmd_content += table_end
                qmd_content += "\n\n{{< pagebreak >}}\n\n"

                # No separate answering sheet is needed
                continue
            else:
                qmd_content += "```{=latex}\n\
{\n\
\Large\n\
```\n\n"

                for index, question in enumerate(questions):
                    qmd_content += f"{index + 1}. {question['question']}\n\n"

                    if "choices" in question:
                        for c_index, choice in enumerate(question["choices"]):
                            letter = lingquiztics.tools.index_to_letter(c_index).upper()
                            qmd_content += f"{letter}.  {choice}\n"
                
                    qmd_content += "\n\
```{=latex}\n\
\\filbreak\n\
```\n\n\n"
            
                qmd_content += "```{=latex}\n\
}\n\
```\n\n"

                # Add pagebreak
                qmd_content += "\n\n{{< pagebreak >}}\n\n"

                qmd_content += lingquiztics.tools.render_header(quiz_round, team_name)

        qmd_content += "```{=latex}\n\
\\begingroup\n\
{\Huge\n\
\\setlength{\\tabcolsep}{20pt}\n\
\\renewcommand{\\arraystretch}{1.5}\n\
\\begin{tabularx}{\\textwidth}{|c|X|}\n\
\hline\n"

        for index, question in enumerate(questions):
            row_content = ""

            if key:
                # Regular answesr
                if "choices" not in question:
                    corrector_explanation = ""
                    prefix = ""
                    if "corrector_note" in question:
                        corrector_explanation = f"\\color{{gray}}~({question['corrector_note']})\\color{{black}}"
                        prefix = "\\Large "

                    row_content = f"{prefix}{question['answer']}{corrector_explanation}"
                # MC answer
                else:
                    correct_index = question["choices"].index(question["answer"])
                    correct_letter = lingquiztics.tools.index_to_letter(correct_index).upper()
                    row_content = f"{correct_letter}"

            elif "choices" in question:
                row_content = " \\hspace{0.5cm} ".join([ lingquiztics.tools.index_to_letter(i).upper() 
                    for i in range(len(question["choices"])) ])

            qmd_content += f"{index + 1} & {row_content} \\\\ \\hline\n"

        qmd_content += "\\end{tabularx}\n\
}\n\
\\endgroup\n\
```\n\n"

#         if not durante:
#             qmd_content += "```{=latex}\n\
# \\begin{center}\n\
# \\LARGE $\\square$ DOUBLE MY POINTS FOR THIS ROUND\n\
# \\end{center}\n\
# ```"

        if round_no + 1 != len(rounds):
            qmd_content += "\n\n{{< pagebreak >}}\n\n"

    qmd_content += "\n\n{{< pagebreak >}}\n\n"

    with open(TEMP_FILENAME, "wt") as writer:
        writer.write(qmd_content)

if no_chain:
    sys.exit()

subprocess.run(["quarto",
                "render", TEMP_FILENAME,
                "--to", "pdf",
                "-o", args.output_file])

if not args.keep_md:
    os.remove(TEMP_FILENAME)