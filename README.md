📱 Kabaddi WhatsApp Bot — FastAPI + LangChain + WhatsApp Cloud API

This project is a conversational WhatsApp chatbot that answers queries about Kabaddi data using a LangChain-powered SQL database backend.
Built using:

    FastAPI: Web framework

    LangChain: Natural Language to SQL translation

    WhatsApp Cloud API: Chat interface

    Google Gemini API: For SQL query generation

    Render / Ngrok / GitHub: Hosting & deployment

🚀 Features

    Answer Kabaddi-related questions from WhatsApp

    Translates natural language queries into SQL

    Uses Excel data (SKDB.xlsx) as the database source

    Can be deployed on Render or run locally using ngrok

    Easily switch between developer testing and production WhatsApp usage

🔧 Project Structure

kabaddi-whatsapp-bot/
├── app.py                   # Main FastAPI app (WhatsApp + Kabaddi bot)
├── requirements.txt          # Required Python libraries
├── SKDB.xlsx                 # Kabaddi dataset
├── modules/                  # LangChain modules
│   ├── llm_config.py
│   ├── prompts.py
│   ├── query_cleaner.py
│   ├── sheet_loader.py
│   ├── sqlite_loader.py
│   ├── logging_config.py

⚙️ Environment Variables

The app reads sensitive tokens and API keys from environment variables.
Variable	Description
ACCESS_TOKEN	WhatsApp Cloud API token
PHONE_NUMBER_ID	WhatsApp Business phone number ID
VERIFY_TOKEN	Token used by WhatsApp for webhook verification (set to 12345 by default)
GOOGLE_API_KEY	Google Gemini API key for LangChain
🔹 Setting Environment Variables Locally

On PowerShell:

$env:ACCESS_TOKEN="EAA...."
$env:PHONE_NUMBER_ID="624292667445289"
$env:VERIFY_TOKEN="12345"
$env:GOOGLE_API_KEY="AIza...."
uvicorn app:app --reload --port 8000

On Render:

    Go to your Render service → Environment → Add Environment Variables

    Add all 4 variables as shown in the table.

▶️ Running the Project Locally

    Clone this repository:

git clone https://github.com/pranavshreyas5010/kabaddi-whatsapp-bot.git
cd kabaddi-whatsapp-bot

Install dependencies:

pip install -r requirements.txt

Start FastAPI:

uvicorn app:app --reload --port 8000

Start ngrok:

    ngrok http 8000

    Copy the ngrok URL (e.g., https://abcd-1234.ngrok-free.app)

🔌 Setting Up WhatsApp Cloud API (Meta Developer)

    Go to https://developers.facebook.com/

    Create a new App → Business App

    Add the WhatsApp product to your app

    Under WhatsApp → API Setup:

        Generate a Temporary Access Token

        Copy your Phone Number ID

        Add your personal WhatsApp number as a test phone number

    Under Configuration → Webhooks, set:

        Callback URL: <your-ngrok-or-render-url>/webhook

        Verify Token: 12345

✅ Now your bot will start receiving WhatsApp messages.
🔄 Moving from Testing to Production
Task	Test Mode ✅	Live Mode 🚀
WhatsApp numbers allowed?	Only test numbers	Anyone with WhatsApp
Token	Temporary (expires in 24 hrs)	Permanent System User token
Business verification	Not required	✔️ Required
App live status	In Development	Must switch to Production
Phone number	Provided test number	Registered WhatsApp Business phone
🔑 Step-by-Step to Go Live

    Verify your business in Facebook Business Manager

        Add a business profile and complete Meta's verification process.

    Create a System User & Permanent Token

        Go to Business Settings → Users → System Users

        Create a new System User and generate a permanent access token.

        Give permissions to manage your WhatsApp Business Account.

    Register a Real Phone Number

        Add a verified WhatsApp Business phone number to your WhatsApp Cloud API.

    Switch App Mode to Production

        Go to Meta Developer portal → App Settings → Switch app to Live mode

    Update your Render Environment Variables

        Replace the temporary access token with the permanent one.

⚙️ API Endpoints
Method	Endpoint	Description
POST	/webhook	Receives WhatsApp messages
GET	/webhook	Handles WhatsApp verification flow
POST	/ask	(Optional) Ask questions to Kabaddi bot via Postman or other API clients
🛡️ Security & Best Practices

    Never hardcode API tokens in your source code.

    Always use environment variables for sensitive keys.

    Use HTTPS URLs in production (Render already provides this).

    Keep your WhatsApp API token secret. It gives full access to send messages from your bot.

🔧 Deployment Options
Platform	Notes
Render	✔️ Free tier available, simple deploy
Railway	Simple GitHub deploy, free hobby hours
Fly.io	Free shared VM, global deployments
Heroku	Free tier removed, $5+ plans available
Google Cloud Run	Pay-as-you-go, scalable containers
🛠️ Handover Checklist

✅ Code is in this repo
✅ All API keys are in environment variables on Render
✅ WhatsApp Cloud API set up under your Meta Developer account
✅ SKDB.xlsx is the database file for Kabaddi
✅ LangChain + Gemini are used for SQL generation

If you’re handing this project over:

    Share this GitHub repo.

    Share your Render and Meta Developer account access OR create new accounts.

    Replace tokens and API keys as needed.

🤝 Contributors

Developed by: Pranav Shreyas
Initial Setup, WhatsApp API, LangChain integration, and Deployment.
