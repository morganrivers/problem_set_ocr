This codebase is for uploading psets using gpt4 vision.

Requirements:
 - GPT4 api key
 - pdflatex installed
 - acroread installed (optional, but it's nice for viewing the latex when they are generated)

Tested on Debian. Your mileage may vary.

Usage:
1. rename the example_data/ to data/. Add your api key in the `data/params.json` file.

2. Get a bunch of images of your pset and download them to a folder within `psets/` subfolder

3. Note: to get out of a compile error and have gpt4 try again to generate valid latex, just enter "x" and that exits pdflatex in a civilized way.

Also! Useful command (unrelated to codebase):
```
python -c "import subprocess; subprocess.run(['pdflatex', 'output.tex'], check=True)"
```
