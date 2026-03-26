# Standing Rock Water Data Dashboard — Frontend Guide

This guide covers every page and feature of the Standing Rock Water Data Dashboard website. It is written for someone with no technical background.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Getting Around the Website (Navigation)](#2-getting-around-the-website-navigation)
3. [Home Page](#3-home-page)
4. [Interactive Map](#4-interactive-map)
5. [Custom Graphs](#5-custom-graphs)
6. [About Us Page](#6-about-us-page)
7. [Contact Us Page](#7-contact-us-page)
8. [Data Sources Explained](#8-data-sources-explained)
9. [Using the Website on a Phone or Tablet](#9-using-the-website-on-a-phone-or-tablet)
10. [Troubleshooting & Common Issues](#10-troubleshooting--common-issues)
11. [Glossary](#11-glossary)

---

## 1. Overview

The Standing Rock Water Data Dashboard is a website that displays water and weather data for the Standing Rock Nation and surrounding areas in North Dakota and South Dakota. It pulls data from government agencies and weather networks, then presents it as interactive maps and graphs.

**What the website lets you do:**

- View an interactive map with 28 monitoring stations (dams, water gauges, and weather stations).
- Click on any station to see its data in chart or table form.
- Build custom graphs by choosing a location, a data type (like water level or temperature), and a date range.
- View statistics (averages, minimums, maximums) for the data you select.
- Learn about the Standing Rock Sioux Tribe and the team behind the dashboard.
- Send a message through the contact form.

**What the website does NOT do:**

- It does not require a login for regular visitors. Only the Admin Page (covered in a separate document) requires a login.
- It does not let visitors change or delete any data. The website is view-only for the public.

---

## 2. Getting Around the Website (Navigation)

The navigation bar sits at the top of every page. It contains:

| Menu Item | Where It Goes |
|-----------|---------------|
| **Home** | The main landing page |
| **About Us** | Information about Standing Rock and the team |
| **Services** (dropdown) | Opens a small menu with two options: |
| — Interactive Map | The map page with clickable stations |
| — Custom Graphs | The page where you build your own graphs |

**On a phone or small screen:** The navigation menu collapses into a "hamburger" icon (three horizontal lines) in the top-right corner. Tap it to open the menu, then tap any item to navigate.

---

## 3. Home Page

**URL:** `/` or `/home/`

The Home Page is the first thing visitors see. It introduces the Standing Rock Water Data Dashboard and directs visitors to the main features.

**What's on the page:**

- **Hero Section** — A brief introduction to the Standing Rock community and the purpose of the dashboard.
- **Services Section** — Two main cards:
  - **Interactive Maps** — Click this to go to the map page. It shows a preview and a short description of the feature.
  - **Custom Graphs** — Click this to go to the graph builder page.
- **Contact Footer** — An email link at the bottom for reaching the team.

There are no interactive controls on this page. It serves as a starting point to guide visitors to the map or graph tools.

---

## 4. Interactive Map

**URL:** `/map/`

This is the primary data exploration tool. It shows a full-screen map of North Dakota and South Dakota with 28 color-coded markers, each representing a monitoring station.

### 4.1 Understanding the Map

When the page loads, you'll see:

- A full-screen map centered on the North Dakota / South Dakota border area.
- **28 markers** scattered across the map. Each one is a data collection station.
- A **legend** in the bottom-right corner explaining the marker colors.

### 4.2 Marker Colors

| Color | Station Type | What It Monitors |
|-------|-------------|------------------|
| **Red** | Water Gauge (USGS) | River water levels, flow rates, water temperature |
| **Blue** | Dam | Reservoir water levels, water released through the dam |
| **Green** | Weather Station (Mesonet) | Air temperature, humidity, rainfall |

### 4.3 Stations on the Map

**Gauge Stations (Red):**
Hazen, Stanton, Washburn, Price, Mandan, Bismarck, Judson, Breien, Schmidt, Cash, Wakpala, Whitehorse, Little Eagle

**Dam Stations (Blue):**
Oahe, Big Bend, Fort Randall, Gavins Point, Garrison, Fort Peck

**Weather Stations (Green):**
Fort Yates, Mott, Carson, Linton, Lemmon, McIntosh, Mclaughlin, Mound City, Timber Lake

### 4.4 Viewing Station Data

1. **Click on any marker** on the map.
2. A **pop-up window (modal)** appears showing that station's data.
3. Inside the pop-up, you'll see **tabs** along the top for different data types. For example, a gauge station might have tabs for:
   - Elevation
   - Gauge Height
   - Discharge (water flow)
   - Water Temperature
4. Each tab has two views you can switch between:
   - **Chart** — A line graph showing how the measurement changed over time. You can hover over points on the graph to see exact values.
   - **Table** — The same data shown as a data table.
5. To close the pop-up, click the **X** button in the top-right corner of the pop-up.

### 4.5 Map Controls

- **Zoom in/out:** Use the scroll wheel on your mouse, or pinch on a touchscreen. You can also use the + and - buttons on the map.
- **Pan (move around):** Click and drag the map, or swipe on a touchscreen.
- **Search:** There is a search bar where you can type a station name to find it quickly. If the station exists, its pop-up will open. If not, you'll see a message saying it wasn't found.

### 4.6 Interacting with Graphs in the Pop-Up

The graphs inside the pop-up are interactive (powered by Plotly). When you hover over a graph, a toolbar appears in the top-right corner with these buttons:

| Button | What It Does |
|--------|-------------|
| **Camera icon** | Downloads the graph as a PNG image (saves to your Downloads folder) |
| **Magnifying glass (+)** | Zoom into a section — click and drag to select an area |
| **Magnifying glass (-)** | Zoom out |
| **Arrows (↔)** | Pan/scroll across the graph |
| **House icon** | Reset the graph to its original view |

---

## 5. Custom Graphs

**URL:** `/maptabs/`

This page lets you build your own graphs by choosing exactly what data you want to see, for which location, and over what time period.

### 5.1 How to Build a Custom Graph

**Step 1: Pick a Location**

At the top of the page, you'll see a row of clickable buttons (chips), each showing a station name. Click one to select it. The selected station will be highlighted.

**Step 2: Pick a Data Type**

After selecting a location, a dropdown menu labeled "Data Type" will appear with the measurements available for that station. Options vary by station type:

- **Gauge stations** might show: Gauge Height, Elevation, Discharge, Water Temperature
- **Dam stations** might show: Elevation, Flow Spill, Flow Powerhouse, Flow Out, Tailwater Elevation
- **Weather stations** might show: Average Air Temperature, Average Relative Humidity, Total Rainfall

**Step 3: Pick a Date Range**

You have two options:

*Option A — Manual dates:*
- Click the **Start Date** field and pick a date.
- Click the **End Date** field and pick a date.

*Option B — Quick range buttons:*
- **Last 7 Days** — Shows the past week
- **Last 30 Days** — Shows the past month
- **YTD** (Year to Date) — Shows from January 1 of this year to today
- **Last 1 Year** — Shows the past 12 months
- **Clear** — Resets the date fields

*Option C — Recent Data button:*
- Click **"Recent Data"** and the system will automatically find the most recent data available for your selected location and data type, then fill in a 30-day window ending at that date.

**Step 4: Check Data Availability**

Below the date fields, you'll see a **data availability indicator** that shows the date range for which data exists. For example: "Data available from 2023-01-15 to 2026-03-10." If you pick dates outside this range, the graph will be empty.

**Step 5: Generate the Graph**

Click the **"Generate"** button. The system will:
1. Look up the data in the database.
2. Create an interactive graph.
3. Display it below the form.

If no data exists for your selection, you'll see a message saying "No data found."

### 5.2 Reading the Graph

The generated graph shows:
- **Horizontal axis (left to right):** Time (dates).
- **Vertical axis (bottom to top):** The measurement value.
- **Line:** Shows how the measurement changed over time.

You can interact with the graph the same way as the map pop-up graphs (hover for values, zoom, pan, download as image).

### 5.3 Statistics Table

Below the graph, a **statistics table** appears showing calculated numbers for the data you selected:

| Statistic | What It Means |
|-----------|---------------|
| **Mean** | The average value across the date range |
| **SD** (Standard Deviation) | How spread out the values are — a small number means values stayed consistent, a large number means they varied a lot |
| **Median** | The middle value when all values are sorted — less affected by extreme highs or lows than the average |
| **Minimum** | The lowest value recorded in the date range |
| **Maximum** | The highest value recorded in the date range |
| **Range** | The difference between the highest and lowest values |

### 5.4 Tips for Custom Graphs

- If you're not sure what dates have data, use the **"Recent Data"** button — it finds the latest available data automatically.
- Keep your date range reasonable. Very large ranges (multiple years) will produce a dense graph that may be harder to read.
- If you see "No data found," try a different date range or check the data availability indicator.
- You can generate multiple graphs in a row. Each new graph replaces the previous one.

---

## 6. About Us Page

**URL:** `/about/`

This page has two sections:

- **Who Are We?** — Background on the Standing Rock Sioux Tribe, with a link to their official website (standingrock.org).
- **What We Do?** — Information about the EPICS HDR team at Purdue University that built this dashboard, with a link to their LinkedIn page.

---

## 7. Contact Us Page

**URL:** `/contactus/`

A simple form for sending a message to the dashboard team.

**Fields:**

| Field | What to Enter |
|-------|---------------|
| **Name** | Your full name |
| **Email** | Your email address (so the team can reply) |
| **Category** | Choose "Comment" or "Concern" from the dropdown |
| **Message** | Write your message |

The **Submit** button stays grayed out until all fields are filled in. Once everything is filled, click Submit to send your message.

---

## 8. Data Sources Explained

The dashboard collects data from several sources. Here's what each one provides:

| Source | Full Name | What Data It Provides |
|--------|-----------|----------------------|
| **USGS** | United States Geological Survey | River water levels (gauge height), water flow (discharge), water temperature at gauge stations along rivers |
| **USACE** | U.S. Army Corps of Engineers | Dam data — reservoir water levels (elevation), water flowing through or over dams |
| **Mesonet** | North Dakota Mesonet Weather Network | Air temperature, relative humidity, rainfall from automated weather stations |
| **NOAA** | National Oceanic and Atmospheric Administration | Weather data — temperature, dew point, wind speed |
| **CoCoRaHS** | Community Collaborative Rain, Hail & Snow Network | Precipitation (rain/snow) measurements from volunteer observers |
| **DANR** | SD Dept. of Agriculture and Natural Resources | Water quality test results (pH, dissolved oxygen, etc.) |
| **Shadehill** | Shadehill Reservoir (USACE) | Water level and flow data specific to Shadehill Reservoir |

**How data gets into the system:**
- Most data is collected **automatically** by scripts that run on a schedule. These scripts connect to the government agencies' websites, download the latest numbers, and store them in the dashboard's database.
- Some data can be entered **manually** through the Admin Page (covered in the Admin Page documentation).

---

## 9. Using the Website on a Phone or Tablet

The website is designed to work on any screen size. Here's what changes on smaller screens:

| Feature | Desktop | Phone/Tablet |
|---------|---------|-------------|
| **Navigation menu** | Full menu bar across the top | Collapses into a hamburger icon (☰) — tap to open |
| **Interactive Map** | Full screen, easy to click markers | Slightly smaller, may need to zoom in to tap markers accurately |
| **Map pop-ups** | Appear to the side of the map | Take up most of the screen for easier reading |
| **Custom Graphs page** | Location buttons in a single row | Buttons wrap into multiple rows |
| **Graphs** | Full-width, detailed view | Full-width, may need to turn phone sideways (landscape) for best view |

**Tips for mobile:**
- Turn your phone sideways (landscape mode) when viewing graphs — you'll see more detail.
- Use pinch-to-zoom on the map to get closer to a station before tapping it.
- Scroll down on pop-ups to see all the graph tabs if they extend below the visible area.

---

## 10. Troubleshooting & Common Issues

### The website won't load

| Possible Cause | What to Do |
|----------------|------------|
| Internet connection is down | Check if other websites work. If not, fix your internet connection first. |
| The server is down | If the site is hosted on Azure, wait a few minutes and try again. If the problem persists, contact the team. |
| Typo in the web address | Make sure you're going to the correct URL. |

### The map is blank or not showing markers

| Possible Cause | What to Do |
|----------------|------------|
| Slow internet connection | Wait a few seconds — the map tiles and markers may still be loading. |
| Browser is outdated | Update your browser to the latest version (Chrome, Firefox, Safari, or Edge). |
| JavaScript is disabled | Make sure JavaScript is enabled in your browser settings. The map and all interactive features require it. |

### I clicked a marker but nothing happened

- Try clicking directly on the marker dot, not just near it.
- On a phone, try zooming in first, then tapping the marker.
- If the pop-up still doesn't appear, refresh the page and try again.

### The graph is empty or says "No data found"

| Possible Cause | What to Do |
|----------------|------------|
| Date range has no data | Check the data availability indicator — make sure your dates fall within the range shown. |
| Too narrow a date range | Try expanding to a wider range (use "Last 30 Days" or "Last 1 Year"). |
| Data source was temporarily unavailable | The data may not have been collected for that period. Try a different date range. |

### The graph looks too crowded or hard to read

- Use the zoom tool (magnifying glass icon) on the graph toolbar to zoom into a specific section.
- Try a shorter date range to spread out the data points.
- Turn your phone sideways for a wider view.

### I can't find a specific station on the map

- Use the search bar on the map page. Type the station name (e.g., "Fort Yates") and it will locate it.
- Check the list of stations in [Section 4.3](#43-stations-on-the-map) above to confirm the station exists in the system.

### The "Recent Data" button isn't working

- Make sure you've selected a location AND a data type first. The button needs both to know what data to look for.
- If it still doesn't work, the system may not be able to reach the database. Try refreshing the page.

### The page looks broken or elements are overlapping

- Try doing a hard refresh:
  - **Windows:** Press `Ctrl + Shift + R`
  - **Mac:** Press `Cmd + Shift + R`
- Clear your browser's cache (saved temporary files). In most browsers: Settings → Privacy → Clear browsing data → Cached images and files.
- Try a different browser.

---

## 11. Glossary

| Term | What It Means |
|------|---------------|
| **Dashboard** | The website itself — a visual display of data, like a car's dashboard shows speed and fuel. |
| **Monitoring Station** | A physical location where instruments measure water or weather conditions. |
| **Marker** | A colored dot on the map representing a monitoring station. |
| **Modal / Pop-up** | A window that appears on top of the page when you click something (like clicking a map marker). |
| **Tab** | A clickable label that switches between different views (like tabs in a filing cabinet). |
| **Chart / Graph** | A visual picture of data, usually a line showing how values change over time. |
| **Data Type / Metric** | The specific thing being measured (e.g., water level, temperature, rainfall). |
| **Date Range** | The time period you're looking at — defined by a start date and an end date. |
| **Gauge Height** | How high the water is at a river gauge station, measured in feet. |
| **Elevation** | The water surface level at a dam or reservoir, measured in feet above sea level. |
| **Discharge** | The volume of water flowing past a point, measured in cubic feet per second. |
| **Tailwater Elevation** | The water level just below (downstream of) a dam. |
| **Flow Spill** | Water released over a dam's spillway. |
| **Flow Powerhouse** | Water released through a dam's power-generating turbines. |
| **Relative Humidity** | How much moisture is in the air, shown as a percentage. 100% means the air is fully saturated. |
| **Precipitation** | Rain, snow, sleet, or hail — any water falling from the sky. |
| **Mean / Average** | All the values added up and divided by how many there are. |
| **Median** | The middle value when all values are lined up from lowest to highest. |
| **Standard Deviation (SD)** | How much the values vary from the average. Small = consistent, Large = variable. |
| **Range** | The difference between the highest and lowest values. |
| **Plotly** | The software that creates the interactive graphs on the website. |
| **Mapbox** | The software that creates the interactive map on the website. |
| **Database** | Where all the data is stored — like a giant organized digital filing cabinet. |
| **Server** | The computer that runs the website and makes it available on the internet. |
| **Azure** | Microsoft's online hosting service where the website lives. |
| **Browser** | The program you use to visit websites (Chrome, Firefox, Safari, Edge). |
| **Cache** | Temporary files your browser saves to load websites faster. Sometimes old cached files cause display problems. |
| **Hard Refresh** | A special refresh that clears cached files and loads everything fresh from the server. |
| **Landscape Mode** | Holding your phone sideways so the screen is wider than it is tall. |

---

*Last updated: March 15, 2026*
