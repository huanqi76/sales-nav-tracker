# investor_connection_tracker

Track new connections that chosen people make on LinkedIn Sales Navigator, and push them to a Google Sheet.

```sh
pip install playwright gspread gspread-formatting && playwright install chromium
export LINKEDIN_USERNAME=... LINKEDIN_PASSWORD=...
python auth/record_login.py   # saves auth/state.json
cp urls.example.txt urls.txt  # add your search URLs
python main.py
```

Copy `auth/gcp_service_account.example.json` to `auth/gcp_service_account.json` and fill in your key. The login state, the key, `urls.txt` and scraped CSVs are git-ignored.

| Path | Contents |
| --- | --- |
| `main.py` | Runs the scrape and the export |
| `scraping/` | Scroll, paginate, and extract names |
| `processing/` | CSV export and Google Sheets sync |
| `auth/record_login.py` | One-time LinkedIn login |
