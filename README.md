# chapkat-final
Receive voice notes interprete them and send feed back

## Deployment to Render.com

1. Create a new Web Service on Render:
   - Go to https://render.com/
   - Click "New +" > "Web Service"
   - Choose "GitHub" or "GitLab" as your repository
   - Connect your repository

2. Configure Environment Variables:
   - In your Render dashboard, go to Environment Variables
   - Add these required variables:
     - `SECRET_KEY`: Your Django secret key
     - `DEBUG`: Set to "false" for production
     - `ALLOWED_HOSTS`: Set to "*" or your specific domain
     - `OPENROUTER_API_KEY`: Your OpenRouter API key
     - `SUNBIRD_API_KEY`: Your Sunbird API key

3. Database Configuration:
   - Create a new PostgreSQL database on Render
   - Connect it to your web service
   - The DATABASE_URL will be automatically injected

4. Build and Deploy:
   - Render will automatically build and deploy your application using the `render.yaml` configuration
   - The first deployment might take a few minutes as it needs to install dependencies

5. Access your application:
   - Once deployed, Render will provide you with a URL
   - Your application will be accessible at this URL

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start the development server:
```bash
python manage.py runserver
```

4. Access the application at http://127.0.0.1:8000/

## API Endpoints

- POST /api/voicebook/api/audio/
  - Upload an audio file and get a transcription
  - Example request:
    ```json
    {
        "audio_file": "<audio_file>",
        "language": "lug"
    }
    ```
  - Example response:
    ```json
    {
        "success": true,
        "transcription": "<transcription>",
        "language": "lug"
    }
    ```

default user
Username: 'default_user'
Email: 'default@chapkat.com'
Password: 'default_password'