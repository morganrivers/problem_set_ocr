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
        continued_latex = response_data["choices"][0]["message"]["content"]
        print("continued_latex")
        print(continued_latex)
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


def get_latex_preamble(page_number):
    latex_preamble = (
        "\\documentclass{article}\n"
        "\\usepackage{fancyhdr}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage{amssymb}\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        "\\fancyhead[R]{\\thepage}\n"
        "\\renewcommand{\\headrulewidth}{0pt}\n"
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


def sort_image_files(folder):
    """Sort image files by date and time extracted from their filenames."""
    image_files = os.listdir(folder)
    pattern = re.compile(r"^signal-\d{4}-\d{2}-\d{2}-\d{4}")

    # Filter files to ensure they match the expected naming convention
    valid_files = [
        file
        for file in image_files
        if pattern.match(file) and file.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    # Sort files based on the sequence number in the filename
    valid_files.sort(key=lambda name: int(name.split("_")[1].split(".")[0]))

    return valid_files


def process_images(selected_folder, openai_api_key):
    """Process each image file within the selected folder."""
    image_files = sort_image_files(PSET_FOLDER / selected_folder)
    print("image_files")
    print(image_files)

    for idx, image_name in enumerate(image_files):
        if image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            page_number = idx + 1
            image_path = PSET_FOLDER / selected_folder / Path(image_name)
            display_image(image_path)
            if input("process this image? (y/n)\n") == "y":
                base64_image = encode_image(image_path)
                while True:
                    # input(f"\nPress enter to send image {page_number} to openai api...\n")
                    latex_preamble = get_latex_preamble(page_number)
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
        print("tex_filename")
        print(tex_filename)
        tex_path = RESULTS_FOLDER / selected_folder / (tex_filename + ".tex")
        print("tex_path")
        print(tex_path)
        pdf_path = RESULTS_FOLDER / selected_folder / (tex_filename + ".pdf")
        print("pdf_path")
        print(pdf_path)
        next_action = save_response_as_tex(response_data, latex_preamble, tex_path)
        if next_action == "success":
            if compile_latex(tex_path):
                print(
                    f"\nCompiled the LaTeX for written page number {page_number}. Continuing.\n"
                )
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


def consolidate_tex_files_sorted(results_folder):
    # This is the final preamble and end document to be used in the consolidated file
    preamble = (
        "\\documentclass{article}\n"
        "\\usepackage{fancyhdr}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage{amssymb}\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        "\\fancyhead[R]{\\thepage}\n"
        "\\renewcommand{\\headrulewidth}{0pt}\n"
        "\\begin{document}\n"
    )
    end_document = "\\end{document}"

    # Initialize a variable to hold the concatenated content
    consolidated_content = ""

    # List and sort all the .tex files in the results folder based on the sequence number
    tex_files = list(results_folder.glob("*signal*.tex"))
    # Assume filenames are like 'signal-YYYY-MM-DD_1234.tex', sort by the integer after the underscore
    print("tex_files")
    print(tex_files)
    tex_files.sort(key=lambda name: int(Path(name).stem.split("_")[-1]))

    # tex_files.sort(key=lambda f: int(re.search(r"_(\d+)", f.stem).group(1)))

    # Loop through the sorted .tex files
    for tex_file in tex_files:
        with open(tex_file, "r") as file:
            lines = file.readlines()

        # Filter out the unwanted lines
        filtered_content = ""
        for line in lines:
            if (
                line.strip().startswith("\\documentclass")
                or line.strip().startswith("\\usepackage")
                or line.strip().startswith("\\pagestyle")
                or line.strip().startswith("\\fancy")
                or line.strip().startswith("\\renewcommand")
                or line.strip().startswith("\\setcounter{page")
                or line.strip() == "\\begin{document}"
                or line.strip() == "\\end{document}"
            ):
                continue
            filtered_content += line

        # Add the filtered content to the consolidated content
        consolidated_content += filtered_content + "\n"

    # Create the final .tex file with the complete content
    final_tex_path = results_folder / "consolidated_output.tex"
    with open(final_tex_path, "w") as file:
        file.write(preamble + consolidated_content + end_document)

    print(f"Consolidated file created at: {final_tex_path}")
    print("compiling...")
    compile_latex(final_tex_path)
    print("compiled")


# Update the call to use the correct results directory, for example:


def main():
    params = load_parameters()
    openai_api_key = params["openai_api_key"]

    subfolders = list_subfolders(PSET_FOLDER)
    selected_folder = display_and_choose_subfolder(subfolders)
    print("selected_folder")
    print(selected_folder)
    (RESULTS_FOLDER / selected_folder).mkdir(parents=True, exist_ok=True)
    process_images(selected_folder, openai_api_key)

    consolidate_tex_files_sorted(RESULTS_FOLDER / selected_folder)


if __name__ == "__main__":
    main()
