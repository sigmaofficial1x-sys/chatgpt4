# MIR Account Manager

A desktop starter app for managing multiple Instagram sessions with isolated browser profiles.

## What is included

- **High-fidelity PyQt6 UI** with a dark SaaS-style layout.
- **Profiles dashboard** containing:
  - Account Name
  - Proxy IP
  - Status (Active / Inactive)
  - Open Browser action
- **Primary action** button: `Add New Profile`.
- **Manual login flow** button: `Launch Login Browser` to open `instagram.com/accounts/login`.
- **SQLite storage** for profile metadata and per-profile browser data directory.
- **Undetected browser launch** using `undetected-chromedriver` and
  `--disable-blink-features=AutomationControlled`.

## Run

```bash
pip install PyQt6 selenium undetected-chromedriver
python app.py
```

## Notes

- Each profile gets a unique `data/profiles/<profile_name>` directory via `--user-data-dir`.
- Session artifacts (cookies/local storage) are preserved in each profile directory after browser close.
- Use `Open Browser` to relaunch a stored profile session.
