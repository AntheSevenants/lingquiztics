import json
import lingquiztics.tools

def load(path):
    with open(path, "rt") as reader:
        content = reader.read()

    return json.loads(content)

def make_text(question):
    return question["description"] + " " + question["question"]

def output_question(question, index):
    qmd_content = ""

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

    if "video" in question:
        video_file = question["video"]
        qmd_content += f"<video src='{video_file}' controls></video>\n\n"

    # Question itself (only displays on advance)
    qmd_content += f"\n\n. . .\n\n{question['question']}\n\n"

    # For multiple choice questions
    if "choices" in question:
        for c_index, choice in enumerate(question["choices"]):
            letter = lingquiztics.tools.index_to_letter(c_index).upper()
            qmd_content += f"{letter}.  {choice}\n"

        qmd_content += "\n\n"

    # Add speaker notes
    qmd_content += f"::: {{.notes}}\n\
{lingquiztics.questions.make_text(question)}.\n\
:::\n\n"
    
    return qmd_content