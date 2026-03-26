# Standing Rock Water Data Dashboard — Admin Page Guide

Welcome! This guide will walk you through everything you need to know about the **Admin Page** of the Standing Rock Water Data Dashboard. It's written in plain, everyday language so you can confidently manage the system without needing a technical background.

---

## Table of Contents

1. [What Is the Admin Page?](#1-what-is-the-admin-page)
2. [How to Access the Admin Page](#2-how-to-access-the-admin-page)
3. [Understanding User Roles](#3-understanding-user-roles)
4. [The Three Tabs of the Admin Page](#4-the-three-tabs-of-the-admin-page)
   - [Console Log Tab](#41-console-log-tab)
   - [Data Entry Tab](#42-data-entry-tab)
   - [User Control Tab](#43-user-control-tab)
5. [Step-by-Step: Common Tasks](#5-step-by-step-common-tasks)
6. [Troubleshooting & Common Issues](#6-troubleshooting--common-issues)
7. [Important Safety Tips](#7-important-safety-tips)
8. [Glossary of Terms](#8-glossary-of-terms)

---

## 1. What Is the Admin Page?

The Admin Page is a special, password-protected area of the Standing Rock Water Data Dashboard. Think of it as the "control room" for the website. From here, you can:

- **View system activity logs** — See what the system has been doing behind the scenes.
- **Manually add data** — Type in new water measurements (like dam levels, weather data, water quality readings) directly into the system.
- **Manage users** — Create new user accounts, change passwords, assign roles, or remove accounts.
- **Run data updates** — Tell the system to go fetch the latest data from its sources (like USGS, NOAA, etc.).

Only authorized people can access this page. Regular visitors to the website will never see it.

---

## 2. How to Access the Admin Page

### Step-by-Step Login

1. Open your web browser (Chrome, Firefox, Safari, Edge — any will work).
2. Go to the website address, and add `/admin/login` at the end.
   - **Example:** If your website is at `www.example.com`, go to `www.example.com/admin/login`
   - If you're running it on your own computer for testing, go to: `http://127.0.0.1:8000/admin/login`
3. You'll see a login screen. Enter your **username** and **password**.
4. Click the **"Sign In"** button.
5. If your credentials are correct, you'll be taken to the Admin Dashboard.

### Logging Out

- Click the **"Logout"** button in the top-right corner of the admin page.
- You'll be taken back to the login screen.
- **Always log out when you're done**, especially on shared computers.

---

## 3. Understanding User Roles

There are two types of admin users. Think of them like different levels of access:

### Admin (Full Access)
- Can see and do **everything** on the admin page.
- Can view logs, add data, run data update scripts, and manage all users.
- This is the highest level of access.

### Data Moderator (Limited Access)
- Can view logs and add data.
- **Cannot** manage users (no access to the User Control tab).
- **Cannot** run data update scripts.
- This role is ideal for someone who only needs to enter data.

### Who Gets Which Role?

| Task | Admin | Data Moderator |
|------|:-----:|:--------------:|
| View system logs | Yes | Yes |
| Add new data entries | Yes | Yes |
| Run data update scripts | Yes | No |
| Create new users | Yes | No |
| Edit or delete users | Yes | No |
| Change other users' passwords | Yes | No |

---

## 4. The Three Tabs of the Admin Page

When you log in, you'll see the admin dashboard with **tabs** across the top (like tabs in a filing cabinet). Each tab gives you access to different tools.

---

### 4.1 Console Log Tab

**What it is:** A live activity feed that shows you what the system is doing behind the scenes. Think of it like a security camera feed, but for the software.

**What you'll see:**
- Text messages that scroll by, showing system activity.
- A **status indicator** that says either:
  - **"Idle"** — The system is not running any tasks right now.
  - **"Running"** — The system is currently updating data.
- A **"Clear Console"** button to erase the log display (this only clears your screen — it doesn't delete any actual data).

**What the messages mean:**
- **Regular messages** (normal text) — Routine updates, like "Fetched data from USGS successfully."
- **Error messages** (highlighted differently) — Something went wrong. For example, "Failed to connect to NOAA." (See the [Troubleshooting](#6-troubleshooting--common-issues) section below for help.)
- **Separator lines** — Just visual dividers to help you read the log more easily.

**How to use it:**
- The log updates automatically every 3 seconds — you don't need to refresh the page.
- Use it to check whether data updates ran successfully.
- If you see error messages, refer to the Troubleshooting section.

**Admin-Only Feature: "Run Script" Button**
- If you are an **Admin**, you'll see a **"Run Script"** button.
- Clicking this tells the system to go fetch fresh data from all of its sources (USGS, NOAA, DANR, etc.).
- After clicking, the status will change to "Running" and you'll see progress messages in the console.
- **Wait for it to finish** before clicking it again. Running it multiple times at once can cause issues.

---

### 4.2 Data Entry Tab

**What it is:** A form that lets you manually type in new data (like water measurements) and save it to the system's database.

**When would you use this?**
- When you have data that wasn't automatically collected (for example, a hand-written field measurement).
- When you need to correct or add a missing data point.

**How to use it — Step by Step:**

1. **Select a table** — Click the dropdown menu labeled "Select Table." You'll see a list of data categories:
   - **cocorahs** — Rain and snow measurements
   - **dam** — Dam water levels, flow rates, and temperatures
   - **mesonet** — Weather station data (temperature, humidity, wind, etc.)
   - **noaa_weather** — National weather service data
   - **shadehill** — Shadehill Reservoir data
   - **usgs** — USGS water gauge readings
   - **water_quality** — Water quality test results (pH, dissolved oxygen, etc.)
   - **DANR** — South Dakota Department of Natural Resources water samples

2. **Fill in the fields** — After selecting a table, a form will appear with fields specific to that data type. Each field will show:
   - The **name** of the data point (e.g., "elevation", "air_temp", "date").
   - The **type** of data expected:
     - **FLOAT** — A number that can have decimals (e.g., `45.7`)
     - **INTEGER** — A whole number (e.g., `100`)
     - **TEXT** — Regular text or a date/time (e.g., `2026-03-15`)

3. **Click "Insert Data"** — This saves the new entry to the database.

4. **Check the result:**
   - A **green success message** means the data was saved correctly.
   - A **red error message** means something went wrong (see Troubleshooting).

**Tips:**
- You don't have to fill in every field — only the ones you have data for.
- For date fields, use the format: `YYYY-MM-DD` (for example, `2026-03-15` for March 15, 2026).
- For date-and-time fields, use: `YYYY-MM-DD HH:MM:SS` (for example, `2026-03-15 14:30:00` for 2:30 PM).
- Double-check your numbers before clicking Insert — once data is inserted, it can't be easily undone from this page.

---

### 4.3 User Control Tab

> **Note:** This tab is only visible to **Admins**. Data Moderators will not see it.

**What it is:** A user management panel where you can create, edit, and delete user accounts.

**What you'll see:**
- A **list of all users** showing:
  - Username
  - Email address
  - Role (Admin or Data Moderator)
  - Whether the account is active (enabled) or inactive (disabled)
  - The date the account was created

**How to Add a New User:**

1. Click the **"Add User"** button.
2. A form will pop up. Fill in:
   - **Username** — The name they'll use to log in (e.g., `jsmith`). Keep it simple, no spaces.
   - **Password** — A strong password. Mix letters, numbers, and symbols.
   - **Email** — Their email address.
   - **Role** — Choose either:
     - **Admin** — Full access to everything.
     - **Data Moderator** — Can only view logs and enter data.
   - **Active** — Check this box to enable the account. Uncheck to create it but keep it disabled.
3. Click **"Save"**.

**How to Edit a User:**

1. Find the user in the list.
2. Click the **"Edit"** button next to their name.
3. You can change:
   - Their **email address**
   - Their **role** (Admin or Data Moderator)
   - Their **password** (leave the password field blank if you don't want to change it)
   - Whether the account is **active** or **inactive**
4. Click **"Save"** to apply changes.

**How to Deactivate (Disable) a User:**

Instead of deleting a user, you can simply **deactivate** their account:
1. Click **"Edit"** next to the user.
2. Uncheck the **"Active"** box.
3. Click **"Save"**.

This keeps their account on record but prevents them from logging in. You can re-activate it later by checking the box again.

**How to Delete a User:**

1. Find the user in the list.
2. Click the **"Delete"** button next to their name.
3. A confirmation message will appear — click **"OK"** to confirm.
4. The user is permanently removed.

> **Warning:** Deleting a user is permanent and cannot be undone. Consider deactivating them instead if you might need to restore their access later.

**Important Rules:**
- You **cannot** change your own role (to prevent accidentally locking yourself out).
- You **cannot** deactivate or delete your own account.
- Only Admins can access this tab.

---

## 5. Step-by-Step: Common Tasks

### "I want to check if the latest data was downloaded successfully"
1. Log in to the admin page.
2. Go to the **Console Log** tab.
3. Look at the most recent messages. You should see messages like "Data fetched successfully" or similar.
4. If you see red/error messages, the download may have failed — see [Troubleshooting](#6-troubleshooting--common-issues).

### "I want to manually update the data right now"
1. Log in as an **Admin**.
2. Go to the **Console Log** tab.
3. Make sure the status shows **"Idle"** (not already running).
4. Click the **"Run Script"** button.
5. Watch the console for progress. Wait until the status goes back to "Idle."
6. If errors appear, see [Troubleshooting](#6-troubleshooting--common-issues).

### "I want to add a water quality measurement by hand"
1. Log in to the admin page.
2. Go to the **Data Entry** tab.
3. Select **"water_quality"** (or **"DANR"**, depending on the data source) from the dropdown.
4. Fill in the fields you have data for (date, location, measurement values).
5. Click **"Insert Data"**.
6. Verify you see a green success message.

### "I need to give someone access to the admin page"
1. Log in as an **Admin**.
2. Go to the **User Control** tab.
3. Click **"Add User"**.
4. Fill in their username, password, email, and choose a role.
5. Make sure **"Active"** is checked.
6. Click **"Save"**.
7. Share the username and password with the person securely (in person or via a secure message — not regular email if possible).

### "Someone left the team and I need to revoke their access"
1. Log in as an **Admin**.
2. Go to the **User Control** tab.
3. Find their name in the user list.
4. Option A: Click **"Edit"**, uncheck **"Active"**, and click "Save" (recommended — you can undo this later).
5. Option B: Click **"Delete"** and confirm (permanent — cannot be undone).

### "I forgot my password"
- There is no "forgot password" button on the admin login page.
- You'll need another Admin to log in and reset your password from the **User Control** tab (by editing your account and setting a new password).
- If no one can access an Admin account, a developer will need to reset it using the system's command line tools.

---

## 6. Troubleshooting & Common Issues

### Problem: "I can't log in"

| Possible Cause | What to Do |
|----------------|------------|
| Wrong username or password | Double-check that you're typing them correctly. Passwords are case-sensitive ("Password" is different from "password"). |
| Account is deactivated | Ask an Admin to check if your account is set to "Active" in the User Control tab. |
| Account was deleted | Ask an Admin to create a new account for you. |
| Website is down | Try refreshing the page. If the website itself isn't loading, there may be a server issue (see below). |

### Problem: "The website isn't loading at all"

- The web server may have stopped running. If you're running it locally, make sure the server is started (see [How to Start the Server](#how-to-start-the-server-if-running-locally) below).
- If the website is hosted online (on Azure), the hosting service may be experiencing issues. Wait a few minutes and try again. If the problem persists, contact your technical support.

### Problem: "I see error messages in the Console Log"

- **"Failed to connect to..."** or **"Connection error"** — The system tried to fetch data from an outside source (like USGS or NOAA) but couldn't reach it. This is usually because:
  - The outside data source is temporarily down. Wait and try again later.
  - Your internet connection is down. Check if other websites work.
- **"Database error"** or **"SQL error"** — Something went wrong when trying to save or read data. This might need a developer's help if it keeps happening.
- **Occasional, one-time errors** are usually nothing to worry about. If the same error keeps appearing every time, contact your technical support.

### Problem: "I clicked 'Run Script' but nothing is happening"

- Check the status indicator — it should say **"Running."**
- The process can take a few minutes depending on how much data needs to be fetched.
- If the status stays on "Idle" after clicking, try refreshing the page and clicking again.
- If it stays stuck on "Running" for more than 10 minutes, something may have gone wrong. Refresh the page. If it still says "Running," contact your technical support.

### Problem: "I inserted data but I don't see it on the main website"

- The main website graphs and maps pull from the same database, so new data should appear when the page is refreshed.
- Try doing a **hard refresh** of the main page: press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac).
- Make sure the data you entered has the correct date — if the date is very old, you may need to adjust the graph's date range to see it.

### Problem: "I can't see the User Control tab"

- This tab is only available to **Admin** users. If you're logged in as a **Data Moderator**, you won't see it.
- If you believe you should have Admin access, ask a current Admin to upgrade your account.

### Problem: "I accidentally entered wrong data"

- The admin page does not have a built-in way to edit or delete individual data entries.
- If you catch the mistake immediately, contact a developer or technical support person who can correct it directly in the database.
- In the future, always double-check your entries before clicking "Insert Data."

### How to Start the Server (If Running Locally)

If you're running the website on your own computer (not on a hosted service):

1. Open your **Terminal** (Mac) or **Command Prompt** (Windows).
2. Navigate to the project folder. For example:
   - Mac/Linux: `cd /path/to/the/project/folder`
   - Windows: `cd C:\path\to\the\project\folder`
3. Activate the virtual environment:
   - Mac/Linux: `source env/bin/activate`
   - Windows: `env\Scripts\activate`
4. Start the server:
   ```
   python manage.py runserver
   ```
5. Open your web browser and go to: `http://127.0.0.1:8000`
6. To access the admin page: `http://127.0.0.1:8000/admin/login`

If you see an error about missing packages, run:
```
pip install django numpy plotly xlsxwriter whitenoise
```
Then try step 4 again.

---

## 7. Important Safety Tips

1. **Keep passwords strong.** Use a mix of uppercase letters, lowercase letters, numbers, and special characters. Avoid simple passwords like `password123`.

2. **Don't share your login.** Each person should have their own account. This way, if something goes wrong, you can tell who did what.

3. **Always log out** when you're done, especially if you're on a shared computer.

4. **Be careful with data entry.** Double-check your numbers before clicking "Insert Data." There's no easy "undo" button.

5. **Don't click "Run Script" multiple times.** Wait for the current run to finish before starting another one. You'll know it's finished when the status goes back to "Idle."

6. **Deactivate instead of deleting** users when possible. This lets you restore access later if needed.

7. **Keep at least one Admin account active.** If all Admin accounts are deleted or deactivated, no one can manage the system without developer help.

---

## 8. Glossary of Terms

| Term | What It Means |
|------|---------------|
| **Admin Page / Dashboard** | The private control panel for managing the website's data and users. |
| **Database** | Where all the data is stored — think of it like a giant digital spreadsheet. |
| **Console Log** | A text feed that shows what the system is doing behind the scenes. |
| **Script** | An automated program that goes out and collects data from sources like USGS, NOAA, etc. |
| **USGS** | United States Geological Survey — provides water gauge and stream data. |
| **NOAA** | National Oceanic and Atmospheric Administration — provides weather data. |
| **DANR** | South Dakota Department of Agriculture and Natural Resources — provides water quality data. |
| **Mesonet** | A network of automated weather stations in North Dakota. |
| **CoCoRaHS** | Community Collaborative Rain, Hail & Snow Network — a citizen science weather network. |
| **USACE / Shadehill** | U.S. Army Corps of Engineers data, specifically for the Shadehill Reservoir. |
| **Table** | A specific category of data in the database (like "dam" or "water_quality"). |
| **Field / Column** | A specific piece of information within a table (like "temperature" or "date"). |
| **FLOAT** | A number that can have decimals (e.g., 98.6). |
| **INTEGER** | A whole number with no decimals (e.g., 42). |
| **TEXT** | Regular text, often used for dates or location names. |
| **Active (account)** | An account that is turned "on" — the user can log in. |
| **Inactive (account)** | An account that is turned "off" — the user cannot log in, but the account still exists. |
| **Role** | The level of access a user has (Admin or Data Moderator). |
| **Server** | The computer (or online service) that runs the website and makes it available to visitors. |
| **Browser** | The program you use to visit websites (Chrome, Firefox, Safari, Edge, etc.). |
| **URL** | The web address you type into your browser (e.g., `www.example.com`). |
| **Virtual Environment** | A self-contained setup on a computer that keeps the website's software separate from other programs. Only relevant if running locally. |
| **Azure** | Microsoft's cloud hosting service where the website can be hosted online. |

---

*Last updated: March 15, 2026*
