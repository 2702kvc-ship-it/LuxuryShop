# LuxuryShop (development)

Quick setup for local development.

1. Create and activate virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in secrets (DB, mail, SECRET_KEY):

```powershell
copy .env.example .env
notepad .env
```

4. Run the app (from the `LuxuryShop` folder):

```powershell
set FLASK_APP=App/app.py  # address of our app
python -m flask run
```

5. If email confirmation is not working yet, manually confirm a newly created account:

```powershell
python -m flask --app app confirm-user user@example.com
```

Replace `user@example.com` with the email address used during registration.

Notes:
- Do NOT commit your `.env` file. It is included in `.gitignore`.
- For sending email via Gmail, create an App Password and set it in `.env`.

Team workflow:
- Create a feature branch before editing code: `git checkout -b feature/your-name`
- Pull the latest `main` regularly: `git pull origin main`
- Push your branch and open a Pull Request when your changes are ready.
