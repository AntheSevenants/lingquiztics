# lingquiztics
Code for automating the KU Leuven Linguistics quiz ("Lingquiztics")

This repository houses all code you need to build your own IRL 'table quiz'. I built this for the KU Leuven linguistics quiz, but you can use this for any table quiz you want.

The linguiztics program generates from a single file:

- the presentation, *with* speaker notes
- the answering sheets
- the correction keys

## How it works

The lingquiztics program generates a [Quarto](https://quarto.org/) document for the slides, the answering sheets and the key. You define your questions once in a json file, and the program does the rest! There is support for multiple choice, audio, video, revision rounds, table rounds and speaker notes.

## Requirements

- Python
- Quarto
- LaTeX

Or you can use the included Dockerfile.

## Defining your questions

### General structure

Your questions should be defined in a JSON file. The structure is as follows:

```json
{
    "round name": [
        { "question": "Who is the architect of the Eiffel Tower?" }
    ]
}
```

The top level is a named object, with round names as keys. The value for each round is a list, with question objects as items.

### Rounds

If you prefix a round name with `_durante`, that round will be processed as a so-called table round. A table round is a round where the questions are given to the quizzers at the beginning of another round on a sheet of paper. They are not offered in the presentation, but are meant to be solved while the other rounds are ongoing. You define your table round at the moment where you want everyone to hand in. The revision for that round will be shown in the presentation. Table rounds can feature images or multiple choice.

### Questions

Questions are defined as objects. Multiple attributes are supported.

- `question`: the question shown in the presentation. *Required.*
- `answer`: the answer to the question. *Required.*
- `choices`: a list of answer choices for multiple choice questions. *Optional.*
- `description`: the preamble for the question, which will be included in the speaker notes. *Optional.*
- `explanation`: the explanation for a specific answer, which will be included in the speaker notes for the revision round. *Optional.*
- `images`: a list of filenames to pictures, which will be shown in the presentation. *Optional.*
- `audio`: a filename for an audio file, which will be included in the presentation. *Optional.*
- `video`: a filename for a video file, which will be included in the presentation. *Optional.*
- `images_revision`: a list of filenames to pictures, which will be shown in the presentation during the revision round. *Optional.*
- `audio_revision`: a filename for an audio file, which will be included in the presentation during the revision round. *Optional.*
- `video_revision`: a filename for a video file, which will be included in the presentation during the revision round. *Optional.*
- `corrector_note`: add a note for the correctors; will be appended after the answer in the key, between brackets. *Optional*
- `corrector_answer`: the answer to the question, appears on the key only. *Optional.*
- `question_general`: add this to the first question of a table round (`durante_`); it will add an overarching question at the top of the page. Useful for image rounds. *Optional*

If specific revision media is not defined, the media for the normal question will be re-used. Make sure your media is accessible from where your presentation is served. The basename of the quiz folder is automatically added, so define paths relative from your questions JSON file.

## Generating presentation and sheets

### Generating the presentation

- `questions`: path to the questions file
- `beamer_header`: the Quarto presentation header
- `--output_file`: output filename for the presentation. Optional.
- `--no_chain`: do not chain the output to Quarto. Optional.
- `--keep_md`: whether to keep the generated qmd file. Optional.

```
python3 make-beamer.py "question.json" "beamer_header.qmd"
```

### Generating the sheets

- `questions`: path to the questions file
- `sheets_header`: the Quarto document header
- `--output_file`: output filename for the sheets. Optional.
- `--no_chain`: do not chain the output to Quarto. Optional.
- `--keep_md`: whether to keep the generated qmd file. Optional.

```
python3 make-sheets.py "question.json" "sheets_header.qmd"
```

## TODO

- ~~Quarto chaining~~
- ~~beamer conversion~~
- ~~question sheet maker~~
- ~~print multiple choice answers on answering sheet~~
- ~~picture support~~
- ~~gallery support~~
- ~~audio support~~
- ~~video support~~
- ~~multiple choice support~~
- ~~speaker notes~~
- ~~revision round~~
- ~~durante round~~
- ~~different media on correction round~~
- ~~explanation on correction round~~
- styling