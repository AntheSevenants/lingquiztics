import json
import lingquiztics.tools

def load(path):
    with open(path, "rt") as reader:
        content = reader.read()

    return json.loads(content)

def make_text(question):
    return question["description"] + " " + question["question"]

def output_question(question, index, revision_round=False, mc_bold=False):
    qmd_content = ""

    if not "question" in question:
        raise Exception("question attribute not found in question")
    
    if revision_round and "answer" not in question:
        raise Exception("answer attribute not found in question")

    # Add question number to slide
    qmd_content += f"## Question {index + 1}\n\n"

    # If there are images in the question, add them all
    if "images" in question:
        for image_file in question["images"]:
            qmd_content += f"![]({image_file})\n"

    if "audio" in question:
        audio_file = question["audio"]
        qmd_content += f"<audio src='{audio_file}' controls></audio>\n\n"

    if "video" in question:
        video_file = question["video"]
        qmd_content += f"<video src='{video_file}' controls></video>\n\n"

    # Question itself (only displays on advance)
    if not revision_round:
        qmd_content += f"\n\n. . ."
    qmd_content += f"\n\n{question['question']}\n\n"

    if not "choices" in question and revision_round:
        qmd_content += f"\n\n. . .\n\n**{question['answer']}**\n\n"
        

    # For multiple choice questions
    if "choices" in question:
        # No incremental for the revision round
        if revision_round:
            qmd_content += "::: {.nonincremental}\n"

        answer_index = question["choices"].index(question["answer"])

        for c_index, choice in enumerate(question["choices"]):
            letter = lingquiztics.tools.index_to_letter(c_index).upper()
            correct_index = question["choices"].index(question["answer"])

            if c_index == correct_index and mc_bold:
                qmd_content += f"{letter}.  **<u>{choice}</u>**\n"
            else:
                qmd_content += f"{letter}.  {choice}\n"

        if revision_round:
            qmd_content += ":::\n"

        qmd_content += "\n\n"

    # Add speaker notes
    qmd_content += f"::: {{.notes}}\n\
{lingquiztics.questions.make_text(question)}.\n\
:::\n\n"
    
    if revision_round and "choices" in question and not mc_bold:
        qmd_content += output_question(question, index, revision_round, mc_bold=True)
    
    return qmd_content