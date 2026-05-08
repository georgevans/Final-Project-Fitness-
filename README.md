# Final-Project-Fitness-

## How to run

1. Run ```cd PyFitness```.
2. Run ```pip install -r requirements.txt```
3. Run ```uvicorn main:app --reload``` to run and ```python3 -m uvicorn main:app --reload```
4. This will run the program.
5. The site will appear on http://localhost:8000 or http://127.0.0.1

## .env
You will need a .env file to run this program containing two things:
A DATABASE_URL value that is the connection url to your postrgres server (One has been provided in this file)
A SECRET_KEY value that is for session security. This can be basically any string but we recomend choosing something completely random and complex

```.env
DATABASE_URL=postgresql://neondb_owner:npg_8BvoEYWZFtx3@ep-twilight-term-abelis6r-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
SECRET_KEY=de80dewhfrc3r.23refew
```

## Ngrok Setup (Mobile / Live Tracker Testing)

### Prerequisites
- A free ngrok account at [ngrok.com](https://ngrok.com)
- ngrok installed on your machine (`brew install ngrok` on Mac, or download from [ngrok.com](https://ngrok.com))

### Steps

1. Log in to your ngrok account and copy your authtoken from the ngrok dashboard.

2. Authenticate ngrok on your machine (one-time setup):
ngrok config add-authtoken YOUR_AUTH_TOKEN

3. Start the FastAPI app locally:
uvicorn main:app --reload --port 8000

4. In a separate terminal, start the ngrok tunnel:
ngrok http 8000

5. Ngrok will display a public HTTPS URL, for example:
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000

6. Open that HTTPS URL on your mobile device's browser.

### Why ngrok is needed

The Live Tracker feature uses the browser's Geolocation API, which modern browsers only allow over a secure (`https://`) connection. Ngrok creates a public HTTPS tunnel to your local server so GPS tracking works on a real mobile device during development.


