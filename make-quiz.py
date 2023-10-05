import json
import argparse
import lingquiztics.questions

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

    for index, question in enumerate(questions):
        if not "question" in question:
            raise Exception("question attribute not found in question")
        
        # Add question number to slide
        qmd_content += f"## Question {index + 1}\n\n"

        # If there are images in the question, add them all
        if "images" in question:
            for image_file in question["images"]:
                qmd_content += f"![]({image_file})\n"

        if "audio" in question:
            audio_file = question["audio"]
            qmd_content += f"<audio src='{audio_file}' controls></audio>\n\n"

        # Question itself (only displays on advance)
        qmd_content += f"\n\n. . .\n\n{question['question']}\n\n"

with open("presentation.qmd", "wt") as writer:
    writer.write(qmd_content)