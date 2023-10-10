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
parser.add_argument('--team_names', type=str, nargs='?', default=None, help='Path to text file with team names (one per line)')
parser.add_argument('--key', type=bool, nargs='?', default=False, help='Whether to print a key sheet')
args = parser.parse_args()

with open(args.sheets_header, "rt") as reader:
    qmd_content = reader.read()

key = args.key is not False

qmd_content = f"{qmd_content}\n\n"

rounds = lingquiztics.questions.load(args.questions)

if not key:
    team_names = [ " " ]
else:
    team_names = [ "key" ]

if args.team_names is not None and not key:
    with open(args.team_names, "rt") as reader:
        team_names = reader.read().split("\n")

for team_name in team_names:
    for round_no, quiz_round in enumerate(rounds):
        print(quiz_round)

        questions = rounds[quiz_round]

        qmd_content += f"```{{=latex}}\n\
\\begin{{tabularx}}{{\\textwidth}}{{c >{{\\raggedleft\\arraybackslash}}X}}\n\
{quiz_round} & \\tiny {team_name}\n\
\\end{{tabularx}}\n\
```\n\n"

        qmd_content += "```{=latex}\n\
\\begingroup\n\
\\setlength{\\tabcolsep}{20pt}\n\
\\renewcommand{\\arraystretch}{1.5}\n\
\\begin{tabularx}{\\textwidth}{|c|X|}\n\
\hline\n"

        for index, question in enumerate(questions):
            row_content = ""
            if key:
                row_content = f"\\small {question['answer']}"

            qmd_content += f"{index + 1} & {row_content} \\\\ \\hline\n"

        qmd_content += "\\end{tabularx}\n\
```\n\n"

        if round_no + 1 != len(rounds):
            qmd_content += "\n\n{{< pagebreak >}}\n\n"

    qmd_content += "\n\n{{< pagebreak >}}\n\n"

    with open("answer_sheets.qmd", "wt") as writer:
        writer.write(qmd_content)