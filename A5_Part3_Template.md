# Assignment 5 — Part 3: User Testing (20 pts)

**Student:** Ankit Deopurkar  
**Tool Name:** Madison Transparency Agent  
**Date:** February 12, 2026

---

## Overview

Conducted three user testing sessions with different participants. Each tester interacted with the deployed Streamlit app and completed a set of tasks while I observed and took notes.

**Streamlit App URL:** https://madison-framework-xselbtfvfdctrdgkv5fkem.streamlit.app/

---

## User Testing Session 1

### Participant Information

| Field | Details |
|-------|---------|
| **Participant ID** | P1 |
| **Name** | Tanmay Chandan |
| **Role / Background** | CS grad student, has some experience with dashboards from a data analytics course last semester |
| **Technical Proficiency** | Intermediate |
| **Date of Session** | February 11, 2026 |
| **Duration** | 14 minutes |
| **Setting** | In-person, my laptop, Snell Library |

### Tasks Given

| # | Task Description | Completed? (Y/N) | Time Taken | Difficulty (1-5) | Notes |
|---|-----------------|-------------------|------------|-------------------|-------|
| 1 | Navigate to the app and read the sidebar "About" section | Y | 1 min | 1 | Found it immediately, clicked the "About" expander on his own |
| 2 | Enable all 4 data sources and run an analysis | Y | 2 min | 2 | All checkboxes were already enabled by default, he just clicked "Run Analysis." Asked me if it mattered which ones were on. |
| 3 | Adjust the anomaly threshold slider to 2.0σ and re-run | Y | 1.5 min | 2 | Found the slider quickly. Noticed the anomaly count dropped and said "oh okay so higher sigma means fewer anomalies" — got the concept right away. |
| 4 | Find the executive summary and identify the system health status | Y | 1 min | 1 | Scrolled down and found the health banner first, then found the executive summary section below the chart. |
| 5 | Download the HTML report | Y | 0.5 min | 1 | Clicked the download button, opened the file in browser. Said it looked "clean." |
| 6 | Locate the anomaly table and identify the highest-severity anomaly | Y | 1.5 min | 2 | Found the table, identified the CRITICAL row. Asked what the difference between HIGH and CRITICAL was — I pointed him to the severity definitions in the executive summary. |

### Observations

- **What went well:**
  1. He understood the overall flow pretty quickly — select sources, hit run, scroll through results. Didn't need hand-holding.
  2. The color-coded health banner at the top was the first thing he noticed after running the analysis. He said it gave him a good "at a glance" idea of what was going on.

- **Pain points / confusion:**
  1. He wasn't sure what "σ" meant on the slider label. He figured it out from context but said "maybe spell out sigma or add a tooltip that explains it in simpler terms."
  2. The Configuration section being an expander confused him slightly — after running the analysis once, when he wanted to change the threshold, he had to re-open the Configuration expander which had collapsed.

- **Unexpected behaviors:**
  1. When he ran the analysis without an OpenAI key configured, the fallback statistical-only output showed up. He didn't realize there was supposed to be an AI-generated summary too. The info message was there but he skipped past it.

- **Verbatim quotes:**
  - "Wait, this actually pulls live news? That's pretty cool, I thought it was all just the CSV data."
  - "The chart is nice but I wish I could hover over the red diamond points and see the exact value and timestamp."

### Post-Test Questions

| # | Question | Response |
|---|----------|----------|
| 1 | On a scale of 1-10, how easy was the app to use? | 8 |
| 2 | What was the most confusing part? | "The sigma slider — I know what standard deviation is but the σ symbol with the multiplier thing wasn't immediately obvious." |
| 3 | What feature did you find most useful? | "The chart with the threshold line. You can visually see which points are anomalies and where the cutoff is." |
| 4 | What would you change or add? | "Maybe add a way to upload your own CSV instead of just using the default URL. Also the news section feels kind of separate from the main analysis." |
| 5 | Would you use this tool in your work? Why or why not? | "Honestly probably not for my coursework, but if I was doing a DevOps internship or something, yeah, I'd use it to get a quick overview of what's going on." |

---

## User Testing Session 2

### Participant Information

| Field | Details |
|-------|---------|
| **Participant ID** | P2 |
| **Name** | Gaurang Patil |
| **Role / Background** | Information Systems student, works part-time as a junior data analyst. Comfortable with Excel and Tableau, some Python. |
| **Technical Proficiency** | Intermediate |
| **Date of Session** | February 11, 2026 |
| **Duration** | 18 minutes |
| **Setting** | Remote, Zoom screen share |

### Tasks Given

| # | Task Description | Completed? (Y/N) | Time Taken | Difficulty (1-5) | Notes |
|---|-----------------|-------------------|------------|-------------------|-------|
| 1 | Navigate to the app and read the sidebar "About" section | Y | 2 min | 1 | Found the sidebar. Read through the About section carefully, asked me what n8n was. |
| 2 | Enable all 4 data sources and run an analysis | Y | 3 min | 3 | Initially only had NAB checked and unchecked the others by accident. Then re-checked them. Was looking for a "submit" or "apply" button before he noticed "Run Analysis" at the bottom. |
| 3 | Adjust the anomaly threshold slider to 2.0σ and re-run | Y | 2 min | 2 | Adjusted the slider. Was surprised he had to scroll back up to click Run Analysis again — expected the app to auto-refresh. |
| 4 | Find the executive summary and identify the system health status | Y | 1.5 min | 2 | Found the yellow/green banner at top. Then scrolled to the executive summary. He read through it carefully and said the summary was "easy to understand." |
| 5 | Download the HTML report | Y | 1 min | 1 | Downloaded it fine. Opened in Chrome and said the formatting looked professional. |
| 6 | Locate the anomaly table and identify the highest-severity anomaly | Y | 2 min | 3 | Took a bit to find the table — scrolled past it initially because the chart was large. Found it on second scroll. Correctly identified the CRITICAL anomaly. Said "the red highlighting helps a lot." |

### Observations

- **What went well:**
  1. He said the executive summary section was his favorite part. As someone who writes reports at work, he appreciated that it was written in "normal language" and not just numbers.
  2. The download buttons made sense to him right away. He mentioned he'd use the JSON export to bring data into Tableau.

- **Pain points / confusion:**
  1. The "Run Analysis" button being at the bottom of the configuration section meant he had to scroll up after changing the threshold. He expected either auto-refresh when changing parameters or a sticky run button.
  2. He wasn't sure what NewsAPI was or whether he needed his own key for it. The "NewsAPI key not configured" message appeared but he didn't know what to do about it.

- **Unexpected behaviors:**
  1. On Zoom screen share the page was a bit slow to load initially (about 5-6 seconds for the Streamlit cold start). He thought it was broken for a second before the UI appeared.

- **Verbatim quotes:**
  - "Oh this is like a report generator. I could see sending this to a manager who doesn't want to look at raw data."
  - "Can I use this with our company's data? Like plug in a different CSV?"

### Post-Test Questions

| # | Question | Response |
|---|----------|----------|
| 1 | On a scale of 1-10, how easy was the app to use? | 7 |
| 2 | What was the most confusing part? | "Finding the Run Analysis button. I kept looking for it near the data source checkboxes but it was below the fold. Also I didn't know what the NewsAPI thing was." |
| 3 | What feature did you find most useful? | "The executive summary. If I could generate something like that for my work dashboards, that would save me a lot of time writing reports." |
| 4 | What would you change or add? | "Maybe auto-run when I change settings instead of making me click the button again. And some explanation of what each data source actually is — like a small description under each checkbox." |
| 5 | Would you use this tool in your work? Why or why not? | "If it worked with our own metrics data, absolutely. The report generation alone would be useful. Right now it's tied to that specific CPU dataset though." |

---

## User Testing Session 3

### Participant Information

| Field | Details |
|-------|---------|
| **Participant ID** | P3 |
| **Name** | Sunny Yadav |
| **Role / Background** | Business administration student, no technical background. Uses basic tools like Google Sheets and PowerPoint. |
| **Technical Proficiency** | Beginner |
| **Date of Session** | February 12, 2026 |
| **Duration** | 22 minutes |
| **Setting** | In-person, campus lounge, his laptop |

### Tasks Given

| # | Task Description | Completed? (Y/N) | Time Taken | Difficulty (1-5) | Notes |
|---|-----------------|-------------------|------------|-------------------|-------|
| 1 | Navigate to the app and read the sidebar "About" section | Y | 3 min | 2 | Took a moment to find the sidebar on mobile-width browser. Once he expanded it, read through the About section and said "okay I think I get what this does." |
| 2 | Enable all 4 data sources and run an analysis | Y | 4 min | 4 | Was confused by the checkboxes at first — asked "what is NAB?" and "what is RSS?" I explained briefly. He checked all four and clicked Run Analysis. |
| 3 | Adjust the anomaly threshold slider to 2.0σ and re-run | N | 3 min | 4 | He moved the slider but didn't know what the number meant. Asked "what does 2.0 sigma mean? Is higher better or worse?" I explained briefly. He moved it to 2.0 and ran again, but said he wouldn't know what value to pick on his own. Marking as N because he needed help understanding the parameter. |
| 4 | Find the executive summary and identify the system health status | Y | 2 min | 2 | The colored banner was easy for him to spot. He read it and said "okay so it's a warning, that makes sense." Found the executive summary and read through it — said it was understandable. |
| 5 | Download the HTML report | Y | 1 min | 1 | No issues. Clicked the button and opened the file. |
| 6 | Locate the anomaly table and identify the highest-severity anomaly | Y | 3 min | 3 | Had to scroll around a bit. Initially thought the chart was the table. Once he found the actual data table, he could read the severity column fine. "Oh okay, CRITICAL is the bad one." |

### Observations

- **What went well:**
  1. Even though he's non-technical, the health status banner and the executive summary were both things he could understand without help. The plain-English language worked well for him.
  2. He liked the color coding throughout — the banner, the anomaly table severity colors, and the red points on the chart all made sense visually.

- **Pain points / confusion:**
  1. A lot of the terminology was unfamiliar — NAB, RSS, sigma, CPU utilization. He said "I feel like this is made for someone who already knows IT stuff." For a non-technical audience, there needs to be more plain-language descriptions.
  2. He didn't understand the chart axes at first. He asked "what does the y-axis mean? Is 80% good or bad?" Once I explained that higher CPU = more strain, it made sense, but it wasn't self-explanatory for him.

- **Unexpected behaviors:**
  1. He accidentally collapsed the Configuration panel and couldn't figure out how to get it back for about 30 seconds. Kept clicking the main area instead of the expander header.

- **Verbatim quotes:**
  - "I like how it tells you what to do at the bottom of the summary. Like, investigate this, set up alerts for that. That's useful even if I don't know the technical details."
  - "What's CPU utilization? Is that like how much the computer is being used?"
  - "The colors make it easy. Green means fine, yellow means watch out, red means something's wrong."

### Post-Test Questions

| # | Question | Response |
|---|----------|----------|
| 1 | On a scale of 1-10, how easy was the app to use? | 5 |
| 2 | What was the most confusing part? | "All the technical terms. Like sigma, NAB, RSS feed — I don't know what any of that is. The actual results were readable though." |
| 3 | What feature did you find most useful? | "The summary at the bottom that tells you what to do. Also the big colored status thing at the top — that's the first thing you see and it tells you immediately if things are okay or not." |
| 4 | What would you change or add? | "Add like a 'beginner mode' or something that hides the technical options and just shows results. Also explain what the data sources are in normal words." |
| 5 | Would you use this tool in your work? Why or why not? | "Probably not because I don't work with server data. But if it could analyze business metrics like sales numbers or website traffic with the same kind of summary, I'd definitely be interested." |

---

## Synthesis (All 3 Sessions)

### Issues Identified

| # | Issue Description | Severity (Low/Med/High) | Frequency (1/3, 2/3, 3/3) | Suggested Fix |
|---|------------------|------------------------|---------------------------|---------------|
| 1 | Sigma (σ) symbol and threshold multiplier not clear to users | Med | 3/3 | Rename to "Sensitivity Level" with Low/Medium/High labels, or add an inline explanation like "Higher = fewer alerts, Lower = more sensitive" |
| 2 | "Run Analysis" button placement — users had to scroll back to re-run after changing parameters | Med | 2/3 | Move the button outside the Configuration expander, or make it sticky at the top of the results area |
| 3 | Technical jargon in data source names (NAB, RSS) and metrics (CPU utilization) not explained | Med | 2/3 | Add short descriptions under each checkbox and a glossary tooltip for the chart y-axis |
| 4 | No explanation of what NewsAPI is or that it needs a key | Low | 2/3 | Add helper text under the NewsAPI checkbox explaining what it is, and make the "key not configured" message more user-friendly |
| 5 | Configuration expander collapsing after analysis makes it hard to find settings again | Low | 2/3 | Keep the Configuration section open by default, or add a "Settings" button that's always visible |

### Successes Identified

| # | What Worked Well | Mentioned By |
|---|-----------------|-------------|
| 1 | Color-coded health status banner gives an instant overview | P1, P2, P3 |
| 2 | Executive summary is written in plain English and includes actionable recommendations | P2, P3 |
| 3 | The Plotly chart with threshold line makes anomalies visually obvious | P1, P2 |
| 4 | Download buttons for HTML/JSON/Markdown are easy to find and work well | P1, P2, P3 |
| 5 | The overall look is clean and professional, no clutter | P1, P2 |

### User Language & Terminology

| User Phrase | Context | Potential Use |
|------------|---------|---------------|
| "report generator" | Gaurang describing the overall tool function | Could use in marketing — "AI-powered report generator for infrastructure metrics" |
| "the big colored status thing" | Sunny referring to the health banner | Consider labeling it more explicitly, e.g., "System Status" header |
| "tells you what to do" | Sunny appreciating the recommended actions section | Highlight this as a key feature — "actionable recommendations, not just data" |
| "at a glance" | Tanmay describing the health banner experience | Good UX principle to emphasize — "system health at a glance" |
| "plug in our own data" | Gaurang asking about custom CSV support | Feature request to prioritize — CSV upload capability |

### Key Metrics Summary

| Metric | P1 | P2 | P3 | Average |
|--------|----|----|----| --------|
| Ease of use (1-10) | 8 | 7 | 5 | 6.7 |
| Tasks completed (out of 6) | 6 | 6 | 5 | 5.7 |
| Session duration (min) | 14 | 18 | 22 | 18 |
| Would use in their work? (Y/N) | Conditionally | Yes (with own data) | No (wrong domain) | — |

### Top 3 Action Items for Next Iteration

1. **[Priority: High]** Replace the sigma slider with a more intuitive "Sensitivity" control using plain-language labels (Low / Medium / High) that map to the underlying sigma values.  
   _Why:_ All three testers struggled with the σ notation. Even the intermediate-level users had to pause and think about it. This is the single most common friction point.

2. **[Priority: Medium]** Add brief one-line descriptions next to each data source checkbox (e.g., "NAB CPU Metrics — Server performance data from the Numenta benchmark dataset") and include a glossary tooltip on the chart.  
   _Why:_ Two out of three users didn't know what NAB or RSS meant. Adding context will make the tool accessible to non-technical stakeholders, which is who the executive summary is aimed at anyway.

3. **[Priority: Medium]** Move the "Run Analysis" button to a more prominent, always-visible location outside the collapsible Configuration panel.  
   _Why:_ Two users lost track of the button after scrolling through results. A fixed or more prominent button placement would reduce friction when iterating on settings.

---

*End of Part 3*
