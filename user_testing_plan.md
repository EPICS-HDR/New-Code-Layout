# User Testing Plan — Standing Rock HDR Water Data Platform

## 1. Overview

**Application:** Standing Rock Community Water Data Platform (Django + Mapbox)  
**Testing Scope:** Frontend only (assume all backend APIs are functioning correctly)  
**Target Users:** Standing Rock community members, researchers, and site administrators  
**Platform:** Web browser (desktop and mobile)

### User Personas

| Persona | Description | Key Tasks |
|---------|-------------|-----------|
| **Community Member** | Resident of Standing Rock with basic tech skills | Browse homepage, view map, explore graphs |
| **Researcher** | Data-oriented user who needs specific datasets | Use custom graph dashboard, compare date ranges |
| **Administrator** | Staff managing data and users | Login, run updates, insert data, manage users |
| **Data Moderator** | Staff with limited permissions | Login, view logs, insert data |

---

## 2. Testing Environment & Prerequisites

- **Browsers:** Chrome (latest), Firefox (latest), Safari (latest), Edge (latest)
- **Devices:** Desktop (1920×1080, 1366×768), Tablet (768px width), Mobile (375px width)
- **Server:** Local dev server running at `127.0.0.1:8000`
- **Test Accounts:**
  - Admin account (is_staff=True)
  - Data Moderator account (in "Data Moderator" group)
- **Internet Access:** Required for Mapbox map tiles and external images (CDN)

---

## 3. Features To Test

### Feature 1: Navigation Bar

**Location:** [navbar.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/HTML/navbar.html)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| NAV-01 | Logo links to home | Click the logo in the top-left | Navigates to `/` (homepage) | |
| NAV-02 | "Home" link works | Click "Home" in nav | Navigates to `/` | |
| NAV-03 | "About Us" link works | Click "About Us" in nav | Navigates to `/about` | |
| NAV-04 | Services dropdown appears | Hover over "Services ▼" | Dropdown shows "Interactive Map" and "Custom Graphs" | |
| NAV-05 | Services → Interactive Map | Click "Interactive Map" in dropdown | Navigates to `/map/` | |
| NAV-06 | Services → Custom Graphs | Click "Custom Graphs" in dropdown | Navigates to `/maptabs/` | |
| NAV-07 | Mobile hamburger menu | Resize to ≤640px width, click hamburger icon (☰) | Nav menu expands/collapses | |
| NAV-08 | Mobile dropdown | On mobile, tap "Services ▼" | Dropdown items appear without navigating away | |
| NAV-09 | Close menu on outside click | Open mobile menu, tap outside navbar | Menu closes | |
| NAV-10 | Navbar persists across pages | Navigate between Home, About, Map, Maptabs | Navbar renders consistently on all pages | |

#### Evaluation Criteria
- All links navigate to correct pages
- Dropdown is usable on both desktop (hover) and mobile (tap)
- Hamburger toggle works smoothly on screens ≤640px

---

### Feature 2: Homepage

**Location:** [homepage.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/HTML/homepage.html)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| HOME-01 | Page loads successfully | Navigate to `127.0.0.1:8000` or `/home/` | Homepage renders with title "Standing Rock Community" | |
| HOME-02 | "Goals" section text | Scroll to "What Are Our Goals?" | Section displays description about Standing Rock Reservation | |
| HOME-03 | "What We Do" section | Scroll to "What We Do" | Section describes providing water data with correct text | |
| HOME-04 | "Services" button navigates | Click "Services" button in Goals section | Page scrolls to the Services card section (anchor `#services`) | |
| HOME-05 | "About Us" button navigates | Click "About Us" button in Goals section | Navigates to the `/about` page | |
| HOME-06 | Interactive Maps card | In Services section, click "Learn more" on Interactive Maps card | Navigates to `/map` | |
| HOME-07 | Custom Graphs card | In Services section, click "Learn more" on Custom Graphs card | Navigates to `/maptabs` | |
| HOME-08 | Images load | Observe all images in Goals and What We Do sections | All images render (from CDN builder.io) with no broken images | |
| HOME-09 | Footer contact email | Scroll to bottom footer | Email link `Epics-hdr@ecn.purdue.edu` is visible and clickable | |
| HOME-10 | Responsive layout | Resize browser to 768px and 375px | Content stacks appropriately, no horizontal overflow | |

#### Evaluation Criteria
- All sections are clearly readable and visually appealing
- Card links route to the correct pages
- Images load without errors (note: relies on external CDN)
- Layout is responsive across all breakpoints

---

### Feature 3: Interactive Map

**Location:** [interactiveMap.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/HTML/interactiveMap.html), [map.js](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/static/js/map.js), [openModals.js](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/static/js/openModals.js)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| MAP-01 | Map loads | Navigate to `/map/` | Mapbox map renders centered on ND/SD area | |
| MAP-02 | Map zoom/pan | Use mouse scroll to zoom, click-drag to pan | Map is interactive, stays within ND/SD bounds | |
| MAP-03 | Legend displays | Look at the legend on the map | Legend shows: Blue = Dam, Red = Gauge, Green = Mesonet | |
| MAP-04 | All 28 markers visible | Zoom out to see full map extent | All 28 markers appear (13 Gauge, 6 Dam, 9 Mesonet) with correct colors | |
| MAP-05 | Click gauge marker (Hazen) | Click the red marker for "Hazen" | Modal opens with graph tabs for Hazen data | |
| MAP-06 | Click dam marker (Oahe) | Click the blue marker for "Oahe Dam" | Modal opens showing Oahe Dam graph tabs | |
| MAP-07 | Click mesonet marker (Fort Yates) | Click the green marker for "Fort Yates" | Modal opens showing Fort Yates data tabs | |
| MAP-08 | Modal close button | Open any location modal, click the × button | Modal closes | |
| MAP-09 | Modal tab switching | Open a modal with multiple data types, click different type tabs | iframe updates to show the selected graph type | |
| MAP-10 | Chart/Table sub-tabs | In a modal, switch between "Chart" and "Table" sub-tabs | Content switches between chart and table views | |
| MAP-11 | Auto-scroll to modal | Click a marker to open a modal | Page smoothly scrolls to reveal the modal content | |
| MAP-12 | Multiple marker clicks | Click marker A, then click marker B | First modal closes, second modal opens | |
| MAP-13 | No-data location | Click a marker with no associated graph data | Modal displays "No graphs available for this location." | |
| MAP-14 | Mobile map usability | On mobile, navigate to `/map/` | Map fills width, legend hides, modals are full-width | |

#### Evaluation Criteria
- Map renders with all markers in correct positions and colors
- Modals open/close cleanly with correct data per location
- Tab switching within modals works without page reload
- Graph iframes load properly within modals

---

### Feature 4: Custom Graph Dashboard (Map Tabs)

**Location:** [maptabs.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/HTML/maptabs.html)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| GRAPH-01 | Page loads | Navigate to `/maptabs/` | Dashboard loads with title "Custom Graph Dashboard" and subtitle | |
| GRAPH-02 | Location tab strip | Observe the horizontal tab strip | All location chips are visible and horizontally scrollable | |
| GRAPH-03 | Select a location | Click a location chip (e.g., "Hazen") | Chip becomes active (highlighted), form heading updates, metric dropdown populates | |
| GRAPH-04 | Switch locations | Click "Hazen" then click "Bismarck" | Active state moves to Bismarck, metrics update accordingly | |
| GRAPH-05 | Metric dropdown populates | Select a location, open the "Data Type" dropdown | Dropdown shows available metrics for that location | |
| GRAPH-06 | Data availability indicator | Select a location and a metric | Text below dropdown shows "Available data: [start] to [end]" | |
| GRAPH-07 | Manual date entry | Type start date: `2024-01-01`, end date: `2024-06-01` | Date fields accept and display the values | |
| GRAPH-08 | Quick range: Last 7 days | Click "Last 7 days" chip | Start date = today − 7 days, End date = today | |
| GRAPH-09 | Quick range: Last 30 days | Click "Last 30 days" chip | Start date = today − 30 days, End date = today | |
| GRAPH-10 | Quick range: YTD | Click "YTD" chip | Start date = Jan 1 of current year, End date = today | |
| GRAPH-11 | Quick range: Last 1 year | Click "Last 1 year" chip | Start date = today − 1 year, End date = today | |
| GRAPH-12 | Quick range: Clear | Click "Clear" chip | Date fields reset to default (empty or original values) | |
| GRAPH-13 | Generate graph | Select location, metric, dates → click "Generate" | Graph renders in an iframe below the form | |
| GRAPH-14 | Recent Data button | Select location + metric → click "Recent Data" | System queries latest date from DB, fills dates, auto-generates graph | |
| GRAPH-15 | Recent Data without selection | Click "Recent Data" with no location/metric selected | Dates fill with last 30 days; info message prompts to select location/metric | |
| GRAPH-16 | Validation: future start date | Set start date to a future date → click Generate | Error: "Start date cannot be in the future." | |
| GRAPH-17 | Validation: future end date | Set end date to a future date → click Generate | Error: "End date cannot be in the future." | |
| GRAPH-18 | Validation: start > end | Set start date after end date → click Generate | Error: "Start date must be earlier than end date." | |
| GRAPH-19 | No data available | Select a location/metric/date range with no data → Generate | Info message: "No graph is available for [location]…" | |
| GRAPH-20 | Server error handling | Force a server error (if testable) → Generate | Error message: "Server error while generating the graph (500)." | |
| GRAPH-21 | Graph iframe auto-resize | Generate a graph | iframe height adjusts to fit graph content | |
| GRAPH-22 | Scroll to graph | Generate a graph | Page smoothly scrolls to show the rendered graph | |
| GRAPH-23 | Responsive form layout | Resize to ≤980px | Form fields stack to single column | |
| GRAPH-24 | Tab strip scroll | On narrow screens with many locations | Tab strip scrolls horizontally | |

#### Evaluation Criteria
- Location selection correctly populates metrics and availability info
- All quick-range buttons calculate correct date ranges
- Validation catches all invalid date scenarios with clear error messages
- Graphs render correctly in iframes and are interactive (Plotly)
- Error states are handled gracefully with user-friendly messages

---

### Feature 5: About Page

**Location:** [about.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/HTML/about.html)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| ABOUT-01 | Page loads | Navigate to `/about/` | Page renders with "About Us" header | |
| ABOUT-02 | Standing Rock section | Read "Who Are We?" section | Content about the Standing Rock Sioux Tribe is visible | |
| ABOUT-03 | HDR Team section | Read "What We Do?" section | Content about EPICS HDR team and Purdue EPICS | |
| ABOUT-04 | External link: Standing Rock | Click "Learn more" under Standing Rock section | Opens `https://www.standingrock.org/` (external) | |
| ABOUT-05 | External link: LinkedIn | Click "Learn more" under HDR Team section | Opens LinkedIn page for EPICS HDR | |
| ABOUT-06 | Images load | Observe section images | Standing Rock tribe image (CDN) and Purdue arch image (static) both load | |
| ABOUT-07 | Footer contact | Check bottom footer | Email link `Epics-hdr@ecn.purdue.edu` present | |
| ABOUT-08 | Mobile responsive | Resize to 640px and 375px | Content stacks, text is readable, images resize | |

#### Evaluation Criteria
- All text content is accurate and properly formatted
- External links open correctly (preferably in new tab)
- Both CDN and local static images render

---

### Feature 6: Contact Us Page

**Location:** [contactus.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/HTML/contactus.html)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| CONTACT-01 | Page loads | Navigate to `/contactus/` | Contact form renders with "Contact Us" heading | |
| CONTACT-02 | Submit button initially disabled | Observe submit button on page load | Submit button is disabled (greyed out) | |
| CONTACT-03 | Partial form entry | Fill Name and Email only | Submit button remains disabled | |
| CONTACT-04 | Complete form → enable submit | Fill Name, Email, Category, and Message | Submit button becomes enabled (green) | |
| CONTACT-05 | Category dropdown | Click category dropdown | Shows options: "Comment" and "Concern" | |
| CONTACT-06 | Remove a field → disable submit | After enabling, clear the Name field | Submit button becomes disabled again | |
| CONTACT-07 | Email validation | Enter invalid email (e.g., "notanemail") | Browser shows email validation error on submit | |
| CONTACT-08 | Form hover effect | Hover over the form card | Form slightly lifts (translateY animation) | |
| CONTACT-09 | Mobile layout | Resize to 375px | Form is centered and usable on small screens | |

#### Evaluation Criteria
- Submit button enables/disables reactively based on field completion
- HTML5 validation works for required fields and email format
- Form is accessible and visually appealing

---

### Feature 7: Admin Login

**Location:** [login.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/admin_dashboard/login.html)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| LOGIN-01 | Page loads | Navigate to `/admin/login/` | Login form renders with logo, title, and fields | |
| LOGIN-02 | Valid admin login | Enter valid admin credentials → Submit | Redirects to `/admin/` dashboard | |
| LOGIN-03 | Valid data moderator login | Enter valid data moderator credentials → Submit | Redirects to `/admin/` dashboard | |
| LOGIN-04 | Invalid credentials | Enter wrong username/password → Submit | Error message: "Invalid credentials or insufficient permissions." | |
| LOGIN-05 | Non-privileged user login | Enter credentials for a user with no role → Submit | Error message displayed (user lacks dashboard access) | |
| LOGIN-06 | Empty fields | Click Submit with empty fields | Browser HTML5 validation prevents submission | |
| LOGIN-07 | "Back to site" link | Click "← Back to site" | Navigates to `/` (homepage) | |
| LOGIN-08 | Username autofocus | Load the page | Username field is automatically focused | |
| LOGIN-09 | Visual design | Observe the login page | Gradient glow background, styled card with SVG logo | |

#### Evaluation Criteria
- Authentication works correctly for both Admin and Data Moderator roles
- Invalid logins show clear error messages
- Form usability follows best practices (autofocus, required fields)

---

### Feature 8: Admin Dashboard — Console Log Tab

**Location:** [dashboard.html](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/services/templates/admin_dashboard/dashboard.html), [admin_dashboard.js](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/static/js/admin_dashboard.js)

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| CONSOLE-01 | Tab loads by default | Login as admin, arrive at dashboard | Console Log tab is active, log content loads once | |
| CONSOLE-02 | Log content displays | Wait for log to load | Console box shows log lines from [BackEnd/log.txt](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/BackEnd/log.txt) | |
| CONSOLE-03 | No auto-refresh | Wait on console tab for 10+ seconds | Log does NOT auto-update (no polling) | |
| CONSOLE-04 | Update Log button | Click "Update Log" button | Log content refreshes with latest data | |
| CONSOLE-05 | Run Updates (Admin) | As admin, click "Run Updates" button | Status changes to "Script running…", green dot animates | |
| CONSOLE-06 | Run Updates hidden for Moderator | Login as Data Moderator | "Run Updates" button is not visible | |
| CONSOLE-07 | Clear console | Click "Clear" button | Console shows "Console cleared." for ~5 seconds, then resumes on next Update Log click | |
| CONSOLE-08 | Error line highlighting | If log contains error lines | Lines with "error", "exception" are highlighted with error styling | |
| CONSOLE-09 | Status indicator | Observe status bar below console | Shows "Idle" normally; "Script running…" during updates | |
| CONSOLE-10 | Console auto-scroll | Click "Update Log" when new lines exist | Console scrolls to bottom automatically | |

#### Evaluation Criteria
- Logs load once on page load and then only on manual "Update Log" click
- Admin-only features are hidden for Data Moderator role
- Error lines are visually distinct

---

### Feature 9: Admin Dashboard — Data Entry Tab

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| DATA-01 | Switch to Data Entry tab | Click "Data Entry" tab | Panel shows table selector and "Insert Row" button (disabled) | |
| DATA-02 | Lazy-load tables | First time clicking Data Entry tab | Table dropdown populates with database tables | |
| DATA-03 | Select a table | Choose a table from dropdown | Dynamic input fields appear for each column (name + type) | |
| DATA-04 | Input types match columns | Select table with INT and TEXT columns | Number fields show number inputs, TEXT fields show text inputs | |
| DATA-05 | Insert a valid row | Fill in column values → click "Insert Row" | Success feedback: "✓ Row inserted into [table] successfully." | |
| DATA-06 | Insert logged to file | After successful insert, switch to Console Log → click "Update Log" | Log shows: `[YYYY-MM-DD HH:MM:SS] DATA INSERT by [username]: table="...", data={...}` | |
| DATA-07 | Insert error logged | Force an insert error (e.g. invalid data type) | Log shows: `[YYYY-MM-DD HH:MM:SS] DATA INSERT ERROR by [username]: ...` | |
| DATA-08 | Insert with no data | Click "Insert Row" with all fields empty | Error feedback: "Please fill in at least one field." | |
| DATA-09 | Fields clear after insert | After successful insert | All input fields are cleared | |
| DATA-10 | Feedback auto-dismiss | After success/error message appears | Message disappears after ~6 seconds | |
| DATA-11 | Switch tables | Select Table A, then switch to Table B | Fields update to Table B's columns, previous values clear | |
| DATA-12 | Data moderator access | Login as Data Moderator, go to Data Entry | Tab is accessible and functional | |

#### Evaluation Criteria
- Tables load correctly from the database
- Column fields are dynamically generated with proper input types
- Insert feedback is clear and auto-dismisses
- Both admin and data moderator can insert data

---

### Feature 10: Admin Dashboard — User Control Tab

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| USER-01 | Tab visibility (Admin) | Login as admin | "User Control" tab visible in nav | |
| USER-02 | Tab hidden (Data Moderator) | Login as Data Moderator | "User Control" tab is hidden | |
| USER-03 | User table loads | Click "User Control" tab | Table shows users with Username, Email, Role, Active, Joined, Actions | |
| USER-04 | Role badges | View role column | Shows colored badges: Admin (purple), Data Moderator (blue) | |
| USER-05 | Active status badges | View active column | Shows green "Active" or red "Inactive" badges | |
| USER-06 | Add User — open modal | Click "Add User" button | Modal opens with title "Add User", empty fields | |
| USER-07 | Add User — create | Fill username, password, select role → Save | User created, table refreshes with new user | |
| USER-08 | Add User — no password | Try saving with username but no password | Alert: "Password is required for new users." | |
| USER-09 | Add User — duplicate username | Enter existing username → Save | Error message about duplicate username | |
| USER-10 | Edit User — open modal | Click "Edit" next to a user | Modal opens with title "Edit User", pre-filled data, username disabled | |
| USER-11 | Edit User — change role | Change role from Data Moderator to Admin → Save | User's role updates, table refreshes with new badge | |
| USER-12 | Edit User — update email | Change email → Save | Email updates in the table | |
| USER-13 | Edit User — change password | Enter a new password → Save | Password is updated (verify by logging in as that user) | |
| USER-14 | Delete User — confirm dialog | Click "Delete" next to a user | Confirmation dialog: "Delete user [name]? This cannot be undone." | |
| USER-15 | Delete User — cancel | Click Cancel on confirmation | User is not deleted | |
| USER-16 | Delete User — confirm | Click OK on confirmation | User is removed from the table | |
| USER-17 | Cannot delete self | Click "Delete" next to your own account | Error: "Cannot delete yourself" | |
| USER-18 | Cannot change own role | Click "Edit" on yourself, try changing role → Save | Error: "Cannot change your own role" | |
| USER-19 | Modal close — Cancel btn | Open modal, click Cancel | Modal closes | |
| USER-20 | Modal close — outside click | Open modal, click on the grey overlay | Modal closes | |
| USER-21 | Email field optional | Create user with username + password but no email | User created successfully with blank email | |

#### Evaluation Criteria
- Full CRUD operations work for user management
- Role-based restrictions prevent self-destructive actions
- Modal open/close behavior is smooth
- Data Moderators cannot access this tab at all

---

### Feature 11: Admin Dashboard — Tab Switching & Layout

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| DASH-01 | Topbar displays user info | Login and observe top bar | Shows username and role badge | |
| DASH-02 | Logout link | Click logout icon in top bar | Redirected to `/admin/login/` | |
| DASH-03 | Tab switching | Click Console → Data Entry → User Control | Correct panel shows for each tab, others are hidden | |
| DASH-04 | Active tab styling | Click through tabs | Active tab has highlighted/active styling | |
| DASH-05 | Data Moderator: tabs limited | Login as Data Moderator | Only Console Log and Data Entry tabs visible | |

---

## 4. Cross-Cutting Test Areas

### Responsiveness

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| RESP-01 | Desktop (1920×1080) | Load each page at this resolution | Full layout, side-by-side content, map fills correctly | |
| RESP-02 | Laptop (1366×768) | Load each page at this resolution | Content fits without horizontal scroll | |
| RESP-03 | Tablet (768px) | Load each page at this width | Content reflows, forms stack, map adjusts | |
| RESP-04 | Mobile (375px) | Load each page at this width | Single column, hamburger menu, map full-width | |

### Browser Compatibility

| Test ID | Browser | Steps | Expected Result | Pass/Fail |
|---------|---------|-------|-----------------|-----------|
| COMPAT-01 | Chrome latest | Run full test suite | All features function correctly | |
| COMPAT-02 | Firefox latest | Run full test suite | All features function correctly | |
| COMPAT-03 | Safari latest | Run full test suite | Mapbox and CSS render correctly | |
| COMPAT-04 | Edge latest | Run full test suite | All features function correctly | |

### Accessibility

| Test ID | Test Case | Steps | Expected Result | Pass/Fail |
|---------|-----------|-------|-----------------|-----------|
| A11Y-01 | Keyboard navigation | Tab through each page | All interactive elements are focusable and activatable | |
| A11Y-02 | Alt text on images | Inspect all `<img>` elements | All images have descriptive alt attributes | |
| A11Y-03 | Color contrast | Use contrast checker tool | Text meets WCAG AA contrast ratio (4.5:1) | |
| A11Y-04 | Form labels | Inspect form inputs | All inputs have associated `<label>` elements | |
| A11Y-05 | ARIA attributes | Inspect map tabs and dashboard tabs | Tabs have `role="tablist"` and proper ARIA attributes | |

---

## 5. Evaluation Methodology

### Scoring Rubric (per test case)

| Score | Criteria |
|-------|----------|
| **Pass** | Feature works exactly as expected with no issues |
| **Minor Fail** | Feature works but with cosmetic issues or minor UX friction |
| **Major Fail** | Feature does not work or produces incorrect results |
| **Blocked** | Cannot test due to dependency or environment issue |

### Metrics to Collect

1. **Task Completion Rate** — % of test cases that pass
2. **Error Rate** — Number of Major Fails per feature area
3. **Time on Task** — For key user flows (e.g., generating a graph, adding a user)
4. **User Satisfaction** — Post-test survey (5-point Likert scale) covering:
   - Ease of navigation
   - Clarity of data visualizations
   - Intuitiveness of the graph generation process
   - Overall visual appeal

### Recommended User Testing Session Flow

1. **Introduction (5 min):** Explain the application purpose and testing goals
2. **Guided Tasks (25 min):** Walk through key flows:
   - Navigate from homepage to interactive map → click a location → view graph
   - Use the custom graph dashboard → select location, metric, dates → generate
   - (Admin) Login → view console → insert data → manage a user
3. **Free Exploration (10 min):** Let user explore independently
4. **Debrief Survey (5 min):** Collect satisfaction scores and open feedback

---

## 6. Known Limitations & Items to Watch

> [!WARNING]
> - **External CDN images:** Homepage and About page images load from `cdn.builder.io`. If the CDN is down, images will break.
> - **Mapbox API key:** The interactive map uses a hardcoded Mapbox access token in [map.js](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/static/js/map.js). If the token expires, the map will fail to load.
> - **Search function bug:** In [map.js](file:///d:/UNIVERSITY%20MATERIAL/New-Code-Layout/FrontEnd/static/js/map.js) line 49, there's a typo (`searhTerm` instead of `searchTerm`) that will throw an error when searching for "knife river at hazen nd".
> - **Forecast & Favorites pages:** These are placeholder pages with no implemented functionality — skip testing.
> - **Contact form has no backend:** The Contact Us form lacks a form action and backend handler — submission will not actually send data.

---

## 7. Summary of Test Cases

| Feature Area | # of Test Cases |
|---|---|
| Navigation Bar | 10 |
| Homepage | 10 |
| Interactive Map | 14 |
| Custom Graph Dashboard | 24 |
| About Page | 8 |
| Contact Us | 9 |
| Admin Login | 9 |
| Console Log Tab | 9 |
| Data Entry Tab | 10 |
| User Control Tab | 21 |
| Dashboard Layout | 5 |
| Responsiveness | 4 |
| Browser Compatibility | 4 |
| Accessibility | 5 |
| **Total** | **142** |
