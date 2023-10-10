import argparse
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
args = parser.parse_args()

with open(args.sheets_header, "rt") as reader:
    qmd_content = reader.read()

qmd_content = f"{qmd_content}\n\n"

rounds = lingquiztics.questions.load(args.questions)

for round_no, quiz_round in enumerate(rounds):
    print(quiz_round)

    questions = rounds[quiz_round]

    qmd_content += f"```{{=latex}}\n\
\\begin{{tabularx}}{{\\textwidth}}{{c >{{\\raggedleft\\arraybackslash}}X}}\n\
{quiz_round} & \\tiny De Vuurvretende Badeendjes\n\
\\end{{tabularx}}\n\
```\n\n"

    qmd_content += "```{=latex}\n\
\\begingroup\n\
\\setlength{\\tabcolsep}{20pt}\n\
\\renewcommand{\\arraystretch}{1.5}\n\
\\begin{tabularx}{\\textwidth}{|c|X|}\n\
\hline\n"

    for index, question in enumerate(questions):
        qmd_content += f"{index + 1} & \\\\ \\hline\n"

    qmd_content += "\\end{tabularx}\n\
```\n\n"

    if round_no + 1 != len(rounds):
        qmd_content += "\n\n{{< pagebreak >}}\n\n"


with open("answer_sheets.qmd", "wt") as writer:
    writer.write(qmd_content)