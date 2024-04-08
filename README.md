# chaditt

This repository contains a Flask application designed to receive audio messages through a WhatsApp Business number and
transcribe them into text.
The project leverages the WhatsApp Business API for audio message reception and employs a powerful audio transcription
service to accurately convert speech to text.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes.

### Prerequisites

What things you need to install the software and how to install them:

- A WhatsApp Business account and the associated API credentials
- Audio transcription service credentials (e.g., Google Speech-to-Text, IBM Watson Speech to Text)

### Installation

A step-by-step series of examples that tell you how to get a development environment running:

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/AntonioVentilii/chaditt.git
    ```

2. Install the required Python packages:

    ```bash
   cd chaditt
   pip install -r requirements.txt
   ``` 

3. Configure your WhatsApp Business API credentials and the audio transcription service API keys in the `config.py`
   file.

### Running the Application

To run the application, use the following command from the root directory of the project:

```bash
flask run
```

This will start the Flask development server, making the application accessible at `http://localhost:5000`.

## Usage

Once the application is running, you can send audio messages to your configured WhatsApp Business number.
The application will automatically transcribe these audio messages and you can retrieve the transcriptions via the
application's API or UI (as implemented).

## License

This project is not open source - see the [LICENSE.md](LICENSE.md) file for details.
The source code is available forviewing and reference only.
Unauthorized copying, modification, distribution, or use of this software is strictly
prohibited.
For any inquiries regarding permissible use, please contact me.

## Acknowledgments

- WhatsApp Business API for enabling communication.
- Audio transcription services for providing accurate speech-to-text capabilities.
