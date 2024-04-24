# Spreadsheet Filler

## Google Config (Once globally)

- Create Service Account
- Set Domain-wide Delegation for service-account: https://admin.google.com/ac/owl/domainwidedelegation?rapt=AEjHL4M6r6xdUpudcXkSMOq4U_w0td3_PFwPI5D89iivdr_Sf-0SXHNVDgQJYzWVW9eSA3YqaG8G18J41OtgcIJLaRvbqtSTlgm8A59KZJwaY26273jDlis
- Create OAuth Consent Screen: https://console.cloud.google.com/apis/credentials/consent/edit?project=spreadsheet-421011

## Onetime Setup

- Add `.env` file with OpenAI Key
- Add `oauth.json` with oauth setup

## Everytime Setup

- Setup venv `python -m venv ./.venv`
- Install Dependencies `pip install -r requirements.txt`
- Setup source `source ./.venv/bin/activate`

## Running

- Run a programmable Google Chrome instance `yarn setup:chrome`

## Demo

See [DEMO.md](./DEMO.md)
