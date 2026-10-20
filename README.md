<div align="center">

# Vault Messenger

**Private, encrypted, realtime chat for your circle. One HTML file, no server to run.**

Glass UI · Dark and light · Installable on your phone · Built on Supabase

</div>

## What it does

| | |
|---|---|
| **Chat** | One-to-one chats plus an "Everyone" room, live delivery, history that loads instantly |
| **Replies and reactions** | Swipe right (or tap a message) to reply, react with 6 quick emoji |
| **Edit and delete** | Edit your own messages, delete for everyone or just for you |
| **Read receipts** | Single tick when sent, double tick when read |
| **Presence** | Real online status and a typing indicator |
| **Photos and voice notes** | Photos are resized on your device, voice notes up to 2 minutes, all encrypted |
| **Disappearing messages** | 1 hour, 24 hours or 7 days per chat |
| **Search and export** | Search inside a chat, export it as a text file |
| **Privacy** | PIN lock, auto-lock after inactivity, brute-force delay on wrong PINs |
| **Members** | Admin can add, edit and remove people, and the list syncs to everyone |
| **Comfort** | Dark, light and auto themes, 4 accent colours, sound and desktop alerts |
| **App feel** | Installable PWA, works on phone and desktop |

## Set up in 3 minutes

1. Create a free project at [supabase.com](https://supabase.com).
2. In **Settings → API** copy the **Project URL** and the **anon key**.
3. Open the app, paste them, choose a **vault key** (a long phrase only your group knows), tap **Copy setup SQL**, paste it in Supabase → **SQL Editor** and run it once.
4. Pick who you are and enter your PIN.

Demo members (Alice, Bob and others, PINs 1111 to 6666) are included. Sign in as Alice (admin), open **Members** and replace them with your real people.

On iPhone: Share → **Add to Home Screen**.

## How the privacy works (honestly)

- Every message, photo and voice note is encrypted in the browser with **AES-256-GCM** before it is uploaded. Keys come from your **vault key** with PBKDF2 (100,000 rounds).
- Anyone who knows the vault key can read the chat. Your database host cannot. Share the key only with people you trust.
- PINs lock the app on a device. They are **not** server authentication, and the database rule is open to anyone holding the anon key. Do not use this for anything that needs strong access control.
- Older v1 messages (no vault key) still show up if you leave the vault key empty.

## Files

- `index.html` is the whole app
- `sw.js`, `manifest.webmanifest`, `icons/` make it installable
- `scripts/make-icons.py` regenerates the icons
- `tests/two-user.py` runs two simulated users against a fake database (`pip install playwright && playwright install chromium`, then `python3 tests/two-user.py`)

Crafted by Mahesh Surada.
