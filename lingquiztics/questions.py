import json
import os.path
import lingquiztics.tools

def load(path):
    with open(path, "rt") as reader:
        content = reader.read()

    return json.loads(content)

def make_text(question):
    if not "description" in question:
        return question["question"]

    return f"{question['description']} **{question['question']}**"

def make_text_revision(question):
    text_revision = f"{question['question']}\n\n{question['answer']}"

    if "explanation" in question:
        text_revision += f"\n\n{question['explanation']}"

    return text_revision

def output_question(question, index, revision_round=False, mc_bold=False, base_dir="", dutch=False):
    qmd_content = ""

    if not "question" in question:
        raise Exception("question attribute not found in question")
    
    if revision_round and "answer" not in question:
        raise Exception("answer attribute not found in question")

    # Add question number to slide
    if not dutch:
        qmd_content += f"## Question {index + 1}{{.text-center}}\n\n"
    else:
        qmd_content += f"## Vraag {index + 1}{{.text-center}}\n\n"

    # We can show different media if necessary
    images_key = "images"
    audio_key = "audio"
    video_key = "video"
    if revision_round:
        if "images_revision" in question:
            images_key = "images_revision"
        if "audio_revision" in question:
            audio_key = "audio_revision"
        if "video_revision" in question:
            video_key = "video_revision"

    # If there are images in the question, add them all
    if images_key in question:
        suffix = ""
        if len(question[images_key]) == 1:
            suffix = "{.img-center}"
        elif len(question[images_key]) == 2:
            suffix = "{.img-duo}"
        else:
            suffix = "{.img-small}"

        for image_file in question[images_key]:
            relative_image_file = os.path.join(base_dir, image_file)
            qmd_content += f"![]({relative_image_file}){suffix}\n"

    # Question itself (only displays on advance)
    if not revision_round:
        qmd_content += f"\n\n. . ."
    qmd_content += f"\n\n{question['question']}\n\n"

    # Add audio/video after question (more fair)
    if audio_key in question:
        audio_file = question[audio_key]
        relative_audio_file = os.path.join(base_dir, audio_file)
        qmd_content += f". . .\n\n"
        qmd_content += f"<audio style='display: none;' src='{relative_audio_file}' controls></audio>\n\n"

    if video_key in question:
        video_file = question[video_key]
        relative_video_file = os.path.join(base_dir, video_file)
        qmd_content += f". . .\n\n"
        qmd_content += f"<video src='{relative_video_file}'></video>\n\n"

    if not "choices" in question and revision_round:
        qmd_content += f"\n\n. . .\n\n**{question['answer']}**\n\n"
        

    # For multiple choice questions
    if "choices" in question:
        # No incremental for the revision round
        if revision_round:
            qmd_content += "::: {.nonincremental}\n"

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

    if not revision_round:
        revision_text = lingquiztics.questions.make_text(question)
    else:
        revision_text = lingquiztics.questions.make_text_revision(question)

    # Add speaker notes
    qmd_content += f"::: {{.notes}}\n\
{revision_text}\n\
:::\n\n"
    
    if revision_round and "choices" in question and not mc_bold:
        qmd_content += output_question(question, index, revision_round, mc_bold=True, base_dir=base_dir, dutch=dutch)
    
    return qmd_content