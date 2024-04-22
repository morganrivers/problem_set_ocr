This codebase is for uploading psets using gpt4 vision.

Requirements:
 - GPT4 api key
 - `pdflatex` installed
 - `acroread` installed (optional, but it's nice for viewing the latex when they are generated)

Tested on Debian. Your mileage may vary.

Usage:
1. rename the example_data/ to data/. Add your api key in the `data/params.json` file.

2. Get a bunch of images of your pset and download them to a folder within `psets/` subfolder

3. Now navigate to src/ and run
   ```
   python3 gpt4_to_tex.py
   ```
   That will let you select the pset folder, and then for all the images in the pset
   1. show them to you before you upload them to gpt4
   2. render gpt4's latex version in latex using pdflatex (option to ask gpt4 to try again if the continuation is not valid latex)
   3. show you the rendered pdf with acroread
      
   Note: to get out of a compile error and have gpt4 try again to generate valid latex, just enter "x" and that exits pdflatex in a civilized way.

   Finally, all the latex docs are consolidated into one large latex file which is the latex version of your problem set!

Also! Useful command (unrelated to anything above):
```
python -c "import subprocess; subprocess.run(['pdflatex', 'output.tex'], check=True)"
```
