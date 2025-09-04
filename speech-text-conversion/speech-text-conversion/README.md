# Speech Text Conversion Project

This project is a Flask application that converts text to speech. Users can input text directly or upload a text file, select a language, and receive an audio file of the spoken text.

## Project Structure

- **static/**: Contains static files such as CSS, JavaScript, and images.
- **templates/**: Contains HTML templates for rendering pages. The main template is `index.html`.
- **uploads/**: Directory for storing uploaded text files and generated audio files. This directory is created automatically if it does not exist.
- **main.py**: The main application file that defines the Flask application, sets up routes, and handles text-to-speech conversion.
- **requirements.txt**: Lists the dependencies required for the project, including Flask, gTTS, deep-translator, langdetect, and others.
- **README.md**: Documentation for the project, including setup and running instructions.

## How to Set Up and Run the Application

1. **Create a New Replit**: Go to Replit and create a new Replit project. Choose "Python" as the language.

2. **Upload Files**: Upload all the files and directories from your local project structure (`main.py`, `requirements.txt`, `static/`, `templates/`, `uploads/`, and `README.md`) to the Replit environment.

3. **Install Dependencies**: Open the Shell in Replit and run the command `pip install -r requirements.txt` to install all the required dependencies listed in the `requirements.txt` file.

4. **Set Up Environment Variables**: If your application requires any environment variables (like API keys), set them up in the Secrets section of Replit.

5. **Run the Application**: In the Replit interface, click on the "Run" button. This will start the Flask application. Replit will provide a URL where your application is hosted.

6. **Access the Application**: Open the provided URL in your browser to access your text-to-speech conversion application.

7. **Testing**: Test the application by uploading text files and using the text-to-speech functionality to ensure everything works as expected.

By following these steps, you should be able to successfully deploy your Flask application on Replit.