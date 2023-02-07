# File: prompter.py

"""
This script generates a set of prompts using the OpenAI API, based on the labels detected in an uploaded image.
It uses the following libraries:
- os
- boto3
- openai
- streamlit
- dotenv
"""

import os
import boto3
import openai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def detect_labels(photo, bucket):
    """
    This function detects the labels in the given photo stored in the given S3 bucket.
    It returns a list of labels.
    """
    client = boto3.client("rekognition")
    response = client.detect_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": photo}}, MaxLabels=7
    )
    labellist = []
    for label in response["Labels"]:
        labellist.append(f"{label['Name']}")
    return labellist


def prompt_openai(
    labels, temperature, top_p, frequency_penalty, presence_penalty, prompt_text
):
    """
    This function generates prompts using the OpenAI API, based on the given labels, temperature, top_p, frequency_penalty, presence_penalty, and prompt text.
    It returns a generated text.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"{prompt_text} \n {labels}",
        temperature=temperature,
        max_tokens=256,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    text = response["choices"][0]["text"]
    return text


def upload_photo():
    """
    This function allows users to upload photos to the system, and saves the photos to the specified S3 bucket.
    The function prompts the user to choose photos, and the photos are displayed in the output.
    After uploading the photos, the function returns the name of the uploaded photos.

    Returns:
    -------
    name : str
        The name of the uploaded photos.
    """
    # file uploader to upload photos
    uploaded_files = st.file_uploader(
        "Choose photos to upload",
        accept_multiple_files=True,
        type=["png", "jpeg", "jpg"],
    )

    # if uploaded files are not None, display the uploaded photos
    if uploaded_files is not None:
        st.image(uploaded_files, width=250)
    st.set_option("deprecation.showfileUploaderEncoding", False)

    # submit button to trigger the upload
    submit_button = st.button(label="Give me prompts!")

    # initialize a list to store the names of the uploaded photos
    pic_names = []

    # loop through each uploaded file
    for uploaded_file in uploaded_files:
        # read the content of the file
        file = uploaded_file.read()

        # write the content to a local file with the same name as the original file
        image_result = open(uploaded_file.name, "wb")
        image_result.write(file)

        # add the name of the uploaded file to the list of pic_names
        pic_names.append(uploaded_file.name)

        # close the local file
        image_result.close()

        # if submit button is clicked
        if submit_button:
            # loop through each uploaded file
            for i in range(len(pic_names)):
                # get the name and path of the uploaded file
                name = pic_names[i]
                path = "./" + pic_names[i]

                # connect to the S3 bucket
                s3 = boto3.client("s3")

                # upload the local file to the S3 bucket
                with open(path, "rb") as f:
                    s3.upload_fileobj(f, "picpromptbucket", name)

                # delete the local file
                os.remove(pic_names[i])

            # show success message after uploading
            st.success("Thanks for uploading!")

            # return the name of the uploaded photos
            return name


def delete_photo(name):
    s3_client = boto3.client("s3")
    s3_client.delete_object(Bucket="picpromptbucket", Key=name)


st.set_page_config(
    page_title="Image Prompt Generator", page_icon=":camera:", layout="wide"
)
st.title("Image Prompt Generator")
with st.expander("How does it work?"):
    st.write(
        "This application uses computer vision to identify what appears on the uploaded image, and then creates a set of prompts using Natural Language Processing. Feel free to experiment with the prompt to get different results."
    )

temp_slider = st.sidebar.slider(
    "Temperature",
    0.0,
    1.0,
    0.7,
    help="Controls randomness. Lowering this results in less random completions. As the temperature approaches zero, the model will become deterministic and repetitive.",
)
top_p_slider = st.sidebar.slider(
    "Top P",
    0.0,
    1.0,
    1.0,
    help="Controls diversity via nucleus sampling: 0.5 means half of all likelihood-weighted options are considered.",
)
frequency_penalty_slider = st.sidebar.slider(
    "Frequency Penalty",
    0.0,
    1.0,
    0.0,
    help="How much to penalize new tokens based on their existing frequency in the text so far. Decreases the model's likelihood to repeat the same line verbatim.",
)
presence_penalty_slider = st.sidebar.slider(
    "Presence Penalty",
    0.0,
    1.0,
    0.0,
    help="How much to penalize new tokens based on whether they appear in the text so far. Increases the model's likelihood to talk about new topics.",
)
prompt_text_input = st.sidebar.text_area(
    "Prompt Text",
    max_chars=350,
    height=300,
    value="Make a list of ten interesting and elaborate prompts for image generation based on these labels in an image, start with 'an' and bonus points for adding art styles and artists. Separate instructions with ,",
)

name_uploaded_photo = upload_photo()
if name_uploaded_photo is not None:
    label_list = detect_labels(name_uploaded_photo, "picpromptbucket")
    result = prompt_openai(
        label_list,
        temp_slider,
        top_p_slider,
        frequency_penalty_slider,
        presence_penalty_slider,
        prompt_text_input,
    )
    st.write("Your Prompts:", result)
    delete_photo(name_uploaded_photo)
