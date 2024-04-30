import os
import subprocess
import base64
import requests
from PIL import Image
import json
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
import re

JUST_USE_DUMMY_DATA = False
SHOW_COMPILED_PDF = True
SHOW_PAGE_IMAGE = True

JSON_PARAMETERS_LOCATION = "../data/params.json"

PSET_FOLDER = Path("../psets")
RESULTS_FOLDER = Path("../results")
RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Function to get the response from OpenAI API
def get_response(api_key, latex_preamble, base64_image):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "Provide LaTeX completion which reproduces what is shown on the image in latex. Start your response with \\section and ending with \\end{document}. Be sure to use \\hbox to box final answers. Do not converse with a nonexistent user. Do not offer corrections, only recreate what is written.",
                    }
                ],
            },
            {"role": "user", "content": [{"type": "text", "text": latex_preamble}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }
                ],
            },
        ],
        "max_tokens": 1024,
    }
    print("posting image to openai api...")
    if JUST_USE_DUMMY_DATA:
        return True, latex_preamble
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and len(response_data["choices"]) > 0:
            # continued_latex = response_data["choices"][0]["message"]["content"]
            return response_data, latex_preamble
        print("no choices in response data...")
    else:
        print("error in response:")
        print(response)
    return None, None


# Function to save the LaTeX response as a .tex file
def save_response_as_tex(response_data, latex_preamble, tex_filename):
    if response_data:
        if JUST_USE_DUMMY_DATA:
            continued_latex = "\\section{Lorem ipsum dolor!}\n\\end{document}"
        else:
            continued_latex = response_data["choices"][0]["message"]["content"]
        print("")
        print("continued_latex")
        print(continued_latex)
        print("")
        section_start = continued_latex.find("\\section")
        end_document = continued_latex.find("\\end{document}")
        if section_start != -1 and end_document != -1:
            relevant_text = continued_latex[
                section_start : end_document + len("\\end{document}")
            ]
            final_text = latex_preamble + relevant_text
            print("opening at path")
            print(tex_filename)
            with open(tex_filename, "w") as tex_file:
                tex_file.write(final_text)
            return "success"
        else:
            print("key words for latex not found")
            return "not_found"
    print("response missing")
    return "no_response"


# Function to compile the LaTeX file
def compile_latex(tex_file):
    try:
        subprocess.run(["pdflatex", tex_file.name], cwd=tex_file.parent, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("failed to compile latex")
        return False


def get_latex_preamble(page_number, homework_number):
    """
    CAUTION: used for both giving the llm the start of the given page, and the first page is actually used as the start
    of the document!
    """
    assert page_number >= 1, f"oops, page number starts at 1, but we got {page_number}"
    if page_number == 1:
        latex_preamble = (
            "\\documentclass[fleqn]{article}\n"
            "\\usepackage{fancyhdr}\n"
            "\\usepackage{amsmath}\n"
            "\\usepackage{amssymb}\n"
            "\\pagestyle{fancy}\n"
            "\\fancyhf{}\n"
            "\\fancypagestyle{firstpage}{\\fancyhf{}\\fancyhead[R]{\\textbf{Homework "
            + str(homework_number)
            + " \\\\ Morgan Rivers \\\\ Thermodynamics and Statistical Mechanics \\\\ \\today}}}\n"
            "\\fancyhead[R]{\\thepage}\n"
            "\\renewcommand{\\headrulewidth}{0pt}\n"
            "\\usepackage{enumitem}\n"
            "\\setlist[enumerate]{align=left, labelwidth=*, itemindent=1em, leftmargin=*}\n"
            "\\begin{document}\n"
            "\\thispagestyle{firstpage}\\vspace*{10pt}\\section*{Homework "
            + str(homework_number)
            + "}\\vspace*{10pt}\\subsection*{Exercise 1}\n\n"
        )
    else:
        latex_preamble = (
            "\\documentclass[fleqn]{article}\n"
            "\\usepackage{fancyhdr}\n"
            "\\usepackage{amsmath}\n"
            "\\usepackage{amssymb}\n"
            "\\pagestyle{fancy}\n"
            "\\fancyhf{}\n"
            "\\fancyhead[R]{\\thepage}\n"
            "\\renewcommand{\\headrulewidth}{0pt}\n"
            "\\usepackage{enumitem}\n"
            "\\setlist[enumerate]{align=left, labelwidth=*, itemindent=1em, leftmargin=*}\n"
            "\\begin{document}\n"
            "\\setcounter{page}{" + str(page_number) + "}\n\n"
        )

    return latex_preamble


def load_parameters():
    """Load configuration parameters from a JSON file."""
    with open(JSON_PARAMETERS_LOCATION, "r") as file:
        params = json.load(file)
    return params


def list_subfolders(PSET_FOLDER):
    """List all subdirectories in the given root folder."""
    return [
        f
        for f in os.listdir(PSET_FOLDER)
        if os.path.isdir(os.path.join(PSET_FOLDER, f))
    ]


def display_and_choose_subfolder(subfolders):
    """Display subfolders and prompt the user to choose one."""
    for idx, folder in enumerate(subfolders):
        print(f"{idx + 1}: {folder}")
    while True:
        try:
            folder_choice = int(input("Choose a subfolder by number: ")) - 1
            if 0 <= folder_choice < len(subfolders):
                return Path(subfolders[folder_choice])
            else:
                print(f"Please enter a number between 1 and {len(subfolders)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def modify_filename(filename):
    # Regex to find '_###.' right before the extension
    pattern = r"_(\d{3})\."

    # Check if the filename matches the pattern
    if re.search(pattern, filename):
        # If the filename already has '_###.', return it unchanged
        return filename
    else:
        # If not, add '_000' before the extension
        return re.sub(r"\.", "_000.", filename)


def sort_image_files(folder):
    """
    Sort image files by date and time extracted from their filenames,
    with secondary sorting by optional sequence number.
    """
    image_files = os.listdir(folder)
    pattern = re.compile(r"^signal-\d{4}-\d{2}-\d{2}-(\d{6})(?:_(\d{3}))?\.jpe?g$")

    # Filter files to ensure they match the expected naming convention
    valid_files = [file for file in image_files if pattern.match(file)]

    # Extract and sort files based on the six-digit time and optional sequence number
    valid_files.sort(
        key=lambda name: (
            int(pattern.search(name).group(1)),  # Time part as integer
            int(pattern.search(name).group(2))
            if pattern.search(name).group(2)
            else 0,  # Sequence number or 0 if absent
        )
    )

    return valid_files


def sort_files_by_date_sequence(folder, file_extension, pattern_string):
    """
    Generalized function to sort files by date and time extracted from their filenames,
    with secondary sorting by optional sequence number.
    """
    image_files = os.listdir(folder)
    pattern = re.compile(pattern_string)

    # Filter files to ensure they match the expected naming convention
    valid_files = [
        file for file in image_files if file.lower().endswith(file_extension)
    ]

    # Prepare sorting keys
    new_matches = []
    actually_valid_files = []
    for name in valid_files:
        match = pattern.search(name)
        if match is not None:
            actually_valid_files.append(name)
            new_file = modify_filename(name)
            new_match = pattern.search(new_file)
            new_matches.append(new_match)
    # Extract and sort files based on the six-digit time and optional sequence number
    actually_valid_files.sort(
        key=lambda name: (
            int(pattern.search(name).group(1)),  # Time part as integer
            int(pattern.search(name).group(2))
            if pattern.search(name).group(2)
            else 0,  # Sequence number or 0 if absent
        )
    )

    return actually_valid_files


def process_images(selected_folder, openai_api_key, homework_number):
    """Process each image file within the selected folder."""
    pattern = re.compile(r"^signal-\d{4}-\d{2}-\d{2}-(\d{6})(?:_(\d{3}))?\.jpe?g$")
    image_files = sort_files_by_date_sequence(
        PSET_FOLDER / selected_folder, ".jpeg", pattern
    )
    print("")
    print("image_files")
    print(image_files)
    print("")

    for idx, image_name in enumerate(image_files):
        if image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            page_number = idx + 1
            image_path = PSET_FOLDER / selected_folder / Path(image_name)
            if SHOW_PAGE_IMAGE:
                display_image(image_path)
            if input("process this image? (y/n)\n") == "y":
                base64_image = encode_image(image_path)
                while True:
                    # input(f"\nPress enter to send image {page_number} to openai api...\n")
                    latex_preamble = get_latex_preamble(page_number, homework_number)
                    response_data, latex_preamble = get_response(
                        openai_api_key, latex_preamble, base64_image
                    )
                    next_action = handle_response(
                        response_data,
                        image_name,
                        page_number,
                        latex_preamble,
                        selected_folder,
                    )
                    if next_action == "continue":
                        break  # it seemed to work
                    elif next_action == "repeat":
                        continue  # try again
            else:
                print("skipping image processing.")


def display_image(image_path):
    """Display an image using matplotlib."""
    img = plt.imread(image_path)
    plt.imshow(img)
    plt.axis("off")  # Hide axes
    plt.show()


def view_latex_pdf(pdf_path):
    print("showing pdf...")
    try:
        subprocess.run(["acroread", pdf_path.name], cwd=pdf_path.parent, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False


def handle_response(
    response_data, image_name, page_number, latex_preamble, selected_folder
):
    """Handle the server response for each image."""
    if response_data:
        tex_filename = f"output_{os.path.splitext(image_name)[0]}"
        tex_path = RESULTS_FOLDER / selected_folder / (tex_filename + ".tex")
        pdf_path = RESULTS_FOLDER / selected_folder / (tex_filename + ".pdf")
        next_action = save_response_as_tex(response_data, latex_preamble, tex_path)
        if next_action == "success":
            if compile_latex(tex_path):
                print(
                    f"\nCompiled the LaTeX for written page number {page_number}. Continuing.\n"
                )
                if SHOW_COMPILED_PDF:
                    if not view_latex_pdf(pdf_path):
                        print("issue showing the pdf... continuing anyway")
                return "continue"
            else:
                print("Error compiling LaTeX. Trying api callagain.")
                return "try_again"
        else:
            print("Error saving response as LaTeX. Trying api call again.")
            return "try_again"
    else:
        print("No response data! Trying api call again.")
        return "try_again"


def consolidate_tex_files_sorted(results_folder, homework_number):
    end_document = "\\end{document}"
    consolidated_content = ""

    # Define the pattern for `.tex` files
    pattern = re.compile(r"^output_signal-\d{4}-\d{2}-\d{2}-(\d{6})(?:_(\d{3}))?\.tex$")

    tex_files = sort_files_by_date_sequence(results_folder, ".tex", pattern)

    actual_latex_preamble = get_latex_preamble(
        page_number=1, homework_number=homework_number
    )
    latex_preamble_search_strings_to_remove = [
        "\\documentclass[fleqn]{article}",
        "\\usepackage{fancyhdr}",
        "\\usepackage{amsmath}",
        "\\usepackage{amssymb}",
        "\\pagestyle{fancy}",
        "\\fancyhf{}",
        "\\fancypagestyle{firstpage}{\\fancyhf{}\\fancyhead[R]{\\textbf{",
        "\\fancyhead[R]{\\thepage}",
        "\\renewcommand{\\headrulewidth}{0pt}",
        "\\usepackage{enumitem}",
        "\\setlist[enumerate]{align=left, labelwidth=*, itemindent=1em, leftmargin=*}",
        "\\begin{document}",
        "\\thispagestyle{firstpage}\\vspace*{10pt}\\section*{",
        "\\setcounter{page}{",
        "\\end{document}",
    ]
    for tex_file in tex_files:
        with open(results_folder / tex_file, "r") as file:
            lines = file.readlines()

        filtered_content = ""
        for line in lines:
            if not any(
                line.strip().startswith(preamble)
                for preamble in latex_preamble_search_strings_to_remove
            ):
                filtered_content += line

        consolidated_content += filtered_content + "\n"

    final_tex_path = results_folder / "consolidated_output.tex"
    with open(final_tex_path, "w") as file:
        file.write(actual_latex_preamble + consolidated_content + end_document)

    print(f"Consolidated file created at: {final_tex_path}")
    print("compiling...")
    compile_latex(final_tex_path)
    print("compiled")


# Update the call to use the correct results directory, for example:


def main():
    params = load_parameters()
    openai_api_key = params["openai_api_key"]

    homework_number = int(input("Enter homework number as an integer: "))
    subfolders = list_subfolders(PSET_FOLDER)
    selected_folder = display_and_choose_subfolder(subfolders)
    print("selected_folder")
    print(selected_folder)
    (RESULTS_FOLDER / selected_folder).mkdir(parents=True, exist_ok=True)
    process_images(selected_folder, openai_api_key, homework_number)

    consolidate_tex_files_sorted(RESULTS_FOLDER / selected_folder, homework_number)


if __name__ == "__main__":
    main()
