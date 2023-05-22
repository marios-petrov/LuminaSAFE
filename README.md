# LuminaSAFE

LuminaSAFE is an intelligent voice and text-based communication system powered by artificial intelligence. It provides a seamless and secure way for users to interact with an AI assistant and obtain information or assistance related to whether or not they are in a fraudalent or untrusthworthy situation.

## Overview

LuminaSAFE offers a wide range of features and capabilities to enhance security and support for users. Its key functionalities include real-time speech-to-text transcription, advanced natural language processing, comprehensive conversation tracking, and data analysis. By enabling users to communicate with the AI assistant via phone calls or text messages, LuminaSAFE ensures versatility and accessibility in addressing user needs and concerns.

Whether it's providing information, offering assistance, or identifying potential fraudulent activities, LuminaSAFE aims to empower and protect individuals through its cutting-edge technology and user-friendly interface.

## Getting Started

To use LuminaSAFE, follow these steps:

1. Set up Twilio API credentials by creating an account on the Twilio website.

2. Install the necessary dependencies by running `pip install -r requirements.txt`.

3. Configure the Twilio phone number and API credentials in the `mainController.py` file.

4. Start the application by running `python mainController.py`.

5. Access the application via the provided URL or local development server.

## Usage

- **Phone Calls**: Users can make phone calls to the designated LuminaSAFE phone number and engage in interactive conversations with the AI assistant.

- **Text Messages**: Users can send text messages to the LuminaSAFE phone number and receive responses from the AI assistant.

## File Structure

- **mainController.py**: This is the main controller that handles incoming calls and messages, processes speech and text inputs, and interacts with the AI assistant.

- **gptController.py**: This module integrates with OpenAI's GPT model and provides functions for generating AI responses based on user inputs.

- **databaseController.py**: This module manages the SQLite database and handles storing and retrieving conversation data.

- **streamlitController.py**: This module contains the Streamlit-based web interface for visualizing call statistics and analysis results.

- **phone_calls.db**: This SQLite database file stores the conversation data, including phone numbers, timestamps, and conversation histories.

## Dependencies

LuminaSAFE relies on the following dependencies:

- Flask: A micro web framework for handling HTTP requests and responses.

- Twilio: A cloud communications platform for making and receiving phone calls and text messages.

- OpenAI GPT: An advanced language model used for generating AI responses.

- Streamlit: A Python library for building interactive web applications and visualizations.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgements

- OpenAI's GPT-3.5 model for providing the powerful language processing capabilities.

- Twilio for their robust telecommunication API services.

- Flask, Twilio, and Streamlit open-source communities for their contributions to web development and communication technologies.

- The Python community for creating and maintaining the powerful libraries used in this project.

- The contributors and authors of the resources mentioned in the project, which helped in its development and understanding.






