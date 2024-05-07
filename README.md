This codebase is for uploading psets using gpt4 vision.

Before:
https://private-user-images.githubusercontent.com/73547769/327752124-54dbd87b-0787-4c09-b30d-5a4f15931085.jpeg?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTUxMDM0NjksIm5iZiI6MTcxNTEwMzE2OSwicGF0aCI6Ii83MzU0Nzc2OS8zMjc3NTIxMjQtNTRkYmQ4N2ItMDc4Ny00YzA5LWIzMGQtNWE0ZjE1OTMxMDg1LmpwZWc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQwNTA3JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MDUwN1QxNzMyNDlaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xY2EyMTJiZWEzNGMxZTBhMTM5MTc5NDYzMjE5ZTAyZDYwOGMxMDNmOTRhZjE1YTBjMzFkNGZiNjc0OGJmOGU4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZhY3Rvcl9pZD0wJmtleV9pZD0wJnJlcG9faWQ9MCJ9.4DVZ0V-uNWZY14YqjZb55u0w9k5WbFeWQwR1u0D8fRA
After:
https://private-user-images.githubusercontent.com/73547769/327755061-f328cfc1-41e9-4abb-b75c-da50956c7ae4.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTUxMDM0NjksIm5iZiI6MTcxNTEwMzE2OSwicGF0aCI6Ii83MzU0Nzc2OS8zMjc3NTUwNjEtZjMyOGNmYzEtNDFlOS00YWJiLWI3NWMtZGE1MDk1NmM3YWU0LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDclMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTA3VDE3MzI0OVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTE5NTM5YTA2MmExODFkZjgxM2Y3ZDE1ZTU0Mjc5NWVjYjk4MDViZTFiMDNiYjM0OGZiODRiZWQ0YWI5M2VhNGUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.Fb5mZkiWLQ_vT1jx_FZsVef2lERDmsSkA5IJv7X0XuY


Requirements:
 - GPT4 api key. For me, in adddition to the $20 a month gpt4 charge, gpt4 vision is about $0.01 per query, so the cost will be much less than a dollar per pset.
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
