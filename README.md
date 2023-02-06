# Prompter

This project is a tool to generate interesting and elaborate prompts for image generation based on labels found in an image. The image prompts can be enhanced by adding art styles and artists for bonus points.

# Features
Upload images and get prompts
Control the creativity of the prompt generation with adjustable parameters

Label detection of the uploaded images using AWS Rekognition

Text generation using OpenAI's language model, Davinci

# Getting Started
The following instructions will get you a copy of the project up and running on your local machine.

Prerequisites
You will need to have the following packages installed in your python environment:

boto3

openai

streamlit

PIL

# Installation
Clone this repository to your local machine:

```

git clone https://github.com/mikaelnystroms/prompter.git

```

Set up your virtual environment and install the required packages using pip:

```

pip install -r requirements.txt

```
# Usage
Run the main.py file to launch the application:

```

Streamlit run main.py

```

This will open up a local web interface in your browser where you can upload images and generate prompts. The interface allows you to control the creativity of the prompt generation through adjustable parameters such as temperature, maximum tokens, etc.

