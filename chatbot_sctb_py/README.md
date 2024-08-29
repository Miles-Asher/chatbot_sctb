=====USAGE (subject to change after deployment)===== \
    -   Navigate into chatbot directory in CMD prompt \
    -   Run "pip install -r requirements.txt" to install necessary packages \
    -   Once all packages installed, run "python app.py" \
    -   Ctrl+Click on provided IP address, will open local development server running chatbot \
    -   To use correction feature, send message in format "/correct question | answer" (will prompt for password) \
        -   If correct password provided, new question/answer pair will be added to CSV \

=====FILE CONTENTS===== \
app.py - python code for Flask application \
chatbot.py - python code for chatbot functionality \
requirements.txt - .txt containing used python modules for easy installation \
runtime.txt - .txt specifying python version to use \
templates/ - directory for HTML formatting files \
static/ - directory for CSS styling file, Javascript frontend functionality, and utilized img files\
data/ - directory for CSV file containing question/answer pairs utilized by chatbot \
__pycache__/ - directory containing compiled python binaries \

updated: 8/29/2024
