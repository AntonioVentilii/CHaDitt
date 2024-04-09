# C'Ha Ditt?!

A Flask application designed to receive audio messages through a WhatsApp Business number and transcribe them into text.
The project leverages the WhatsApp Business API for audio message reception and employs OpenAI API audio transcription
service to accurately convert speech to text.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes.

### Prerequisites

What things you need to install the software and how to install them:

- A WhatsApp Business account and the associated API credentials
- An OpenAI API key for the audio transcription service

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

3. Configure your WhatsApp Business API credentials and OpenAI API key:

    - Create a `.env` file in the root directory of the project.
    - Add the following environment variables to the `.env` file:
      ```bash
      GRAPH_API_TOKEN=your_whatsapp_api_key
      MOBILE_ID=your_whatsapp_mobile_id
      OPENAI_API_KEY=your_openai_api_key
      ```
    - Replace `your_whatsapp_api_key`, `MOBILE_ID` and `your_openai_api_key` with your actual data.
    - Save the `.env` file.
    - The application will automatically load these environment variables when it starts.

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
