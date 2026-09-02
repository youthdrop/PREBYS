# Free SD Suite v1

This project contains a polished starter for the Free SD management information database and mobile application.

## Included apps

- **backend/** FastAPI API for authentication, OTP login, password reset, case records, attorney/judge/DA/volunteer records, and reports
- **frontend/** React + Vite admin portal with branded cream / black / white styling
- **mobile/** Expo mobile app for family intake and volunteer sign-up

## Branded v1 updates included

- Professional cream / black / white interface
- Persistent navigation and logout on web admin screens
- Secure login flow with 2-step verification
- Forgot password and reset password screens
- Polished dashboard cards
- Intake form with exact requested fields
- Intake details screen with editable follow-up court information
- Attorney, judge, DA, and volunteer databases
- Reports page for time saved, DA report, judge report, court dates, and intake totals
- Mobile home screen with Families and Volunteers buttons
- Mobile family intake form with required fields
- Mobile volunteer sign-up form with travel-court selectors

## Branding note

No official logo file was included in the project input, so this v1 uses a clean **FS / Free SD** text-based brand mark throughout the web and mobile apps. Replace it later with your official logo asset if you want exact organization branding.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Mobile

```bash
cd mobile
npm install
npm run start
```

## Environment variables

See `.env.example` files in the backend, frontend, and mobile folders.

## Next production steps

- connect real SMS and email providers for OTP and password reset
- add migrations
- add file uploads for intake documents
- add role-based permissions beyond admin delete control
- replace the text mark with the official Free SD logo
