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
