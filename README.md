<div align="center">

  <h1 style="font-size: 2.5rem; font-weight: bold;">
    GenAI Meeting-to-Jira Task Pipeline
  </h1>

  <p style="font-size: 1.2rem; margin-bottom: 20px;">
    <i>A Python automation workflow that ingests meeting audio via Whisper, understands context via GPT-4o, and executes structured updates to Jira.</i>
  </p>

  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenAI-Whisper_&_GPT4o-green?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Jira-REST_API-0052CC?style=for-the-badge&logo=jira&logoColor=white" alt="Jira">
  <img src="https://img.shields.io/badge/Project_Type-Portfolio_Case_Study-orange?style=for-the-badge" alt="Role">

</div>

---

## 📖 Project Overview

**User Story:**
As a PM, I want to automate the translation of verbal meeting decisions into structured Jira tasks/updates, so that I can prioritize active listening and critical thinking over administrative data entry.

**The Problem:**
Throughout my early experience in corporate, I've noticed that valuable context is sometimes lost between verbal meeting discussions and written Jira tickets. Manually updating backlogs is slow and prone to error. 

**The Solution:**
I engineered a **PM Agent AI Pipeline** that transforms unstructured audio files into actionable Jira updates. Unlike basic transcription tools, this project uses a Large Language Model as a reasoning engine to:
1.  **Check Context:** Reads the live Jira board first to avoid creating duplicates.
2.  **Determine Priority:** Detects urgency in speech (e.g., "fire drill") to assign priority levels automatically.
3.  **Structure Data:** Formats the output into a JSON payload for the Jira API.
4.  **Present:** Showcases incoming Jira changes in Terminal, to be approved by User.

---

## 📸 Workflow & Visuals

### 1. Jira Activity
*Showcase of automated activity through Jira API on account.*

<div align="center">
  <img width="440" height="550" alt="Screenshot 2025-12-29 at 2 23 16 PM" src="https://github.com/user-attachments/assets/d2bb7e0e-5df6-4b4d-a666-7527e3d6f43e" width="100%" alt="Terminal Processing">
</div>

<br>

### 2. The Final Approval Layer
*Before any data touches the Jira project, the tool presents a "Proposed Change Plan." I designed this safety layer to prevent AI hallucinations from corrupting project data.*

<div align="center">
  <img width="450" height="440" alt="Screenshot 2025-12-29 at 2 19 10 PM" src="https://github.com/user-attachments/assets/af563e69-d6da-49d8-ac4f-f23d9c74bab0" width="90%" alt="Approval Interface">
</div>

<br>

### 3. Jira Impact (Before vs. After)
*Demonstrating the Agent's ability to update existing tickets and create new ones based on a single meeting recording.*

| **Before: The Stale Board** | **After: Automated Updates** |
| :---: | :---: |
| *Original state of Jira Epic.*<br><img width="1222" height="768" alt="Screenshot 2025-12-29 at 2 24 19 PM" src="https://github.com/user-attachments/assets/c6fd00cd-8ed1-4d0b-837b-af10d1d5649e" width="100%"> | *New Task Created.*<br><img width="1221" height="766" alt="Screenshot 2025-12-29 at 2 22 07 PM" src="https://github.com/user-attachments/assets/42a33eff-e7cd-442a-9201-b0ab3f5bea19" width="100%"> |
| *Original Task KAN-4.*<br><img width="1221" height="768" alt="Screenshot 2025-12-29 at 2 16 29 PM" src="https://github.com/user-attachments/assets/e20a99c4-fdb7-4027-baf4-1e7f0dc01c09" width="100%"> | *New Comment Update & Priority: Low > Medium.*<br><img width="1223" height="768" alt="Screenshot 2025-12-29 at 2 26 28 PM" src="https://github.com/user-attachments/assets/6d808693-f38c-4139-9ebf-b68a9af0a86c" width="100%"> |
| *Original Task KAN-5.*<br><img width="1223" height="768" alt="Screenshot 2025-12-29 at 2 16 16 PM" src="https://github.com/user-attachments/assets/e5981837-b9f6-4699-8a0d-fc0a4931802f" width="100%"> | *New Comment Update & Priority: Low > Highest.*<br><img width="1221" height="768" alt="Screenshot 2025-12-29 at 2 26 17 PM" src="https://github.com/user-attachments/assets/8bbd1fd1-1f7a-4d94-b839-372773f80658" width="100%"> |
| *Original Task KAN-6.*<br><img width="1222" height="767" alt="Screenshot 2025-12-29 at 2 16 04 PM" src="https://github.com/user-attachments/assets/a7b2aa37-4099-41c8-9a89-dfce98c538bc" width="100%"> | *New Comment Update & Priority: Low > Medium.*<br><img width="1222" height="768" alt="Screenshot 2025-12-29 at 2 25 54 PM" src="https://github.com/user-attachments/assets/1105161a-4199-427b-b33c-20fe4d205635" width="100%"> |

---

## 🛠️ System Architecture

This is not a chatbot; it is a sequential data processing pipeline built in Python.

**1. Context Ingestion (`get_project_context`)**
* **Logic:** Before listening to the audio, the script queries the Jira REST API using JQL (`status != Done`).
* **Why:** This loads the current "State of the World" into the AI's context window, allowing it to recognize that "fix the login" refers to the existing ticket `KAN-3`.

**2. Audio Transcribing (`transcribe_audio`)**
* **Tech:** OpenAI Whisper-1 Model.
* **Function:** Converts the `.mp4` or `.mp3` meeting recording into high-fidelity text.

**3. The Reasoning Engine (`run_jira_agent`)**
* **Tech:** GPT-4o with `response_format={"type": "json_object"}`.
* **Prompt Engineering:** I designed a system prompt that acts as a Senior TPM. It is strictly forbidden from creating duplicates and must map vague slang to specific Jira keys.

**4. Execution Layer (`execute_changes`)**
* **Function:** Parses the JSON output and performs authenticated `POST` requests to:
    * Transition Issues (e.g., "To Do" -> "In Progress").
    * Update Priorities.
    * Create new Tasks (automatically linked to a parent Epic).

---

## 🧠 Meeting Audio Testing

**To prove this tool adds real value, I tested it against a challenging script containing vague language and implied tasks.**

**Script**:

“Happy Monday everyone and happy holidays, looking forward to going to Tahoe this year haha.

Alright, let’s get into it. Uh, hope everyone survived the weekend.

So, looking at the board... I want to touch on that email integration piece first. We found out SendGrid is actually too expensive for the volume we're hitting–so we’re gonna pivot to AWS SES instead. Actually, can someone just update that card to mention we need to provision new IAM users? We really can't move forward without those keys.

Also, I noticed that the Confluence page is still blank regarding the key rotation. We promised the Security team we’d have that written down by Friday. It's not a huge deal, but let's try to get a draft in there soon so they get off our backs.

But the real issue that I’d like to address is the Slack alerts. We had a failure last night and the bot didn't say a word. We are literally flying blind right now. If the system goes down, we won't know. We need to treat that as a fire drill—honestly, that’s the most critical thing on the board right now. Let's make sure that gets picked up today.

Oh, and one last thing—Marketing is asking for a frontend. They don't want to query the database manually. We need to build a simple UI, maybe in Streamlit, just so they can see the open rates. Let's get a ticket created for that.”


| **Challenge Category** | **Spoken Phrase (Input)** | **AI Logic & Result** |
| :--- | :--- | :--- |
| **Fuzzy Matching** | *"I want to touch on that email integration piece..."* | **Success:** The Agent correctly identified `KAN-4: API Connection` and appended the note instead of creating a new ticket. |
| **Implicit Priority** | *"We are literally flying blind... treat this as a fire drill."* | **Success:** The Agent interpreted the emotional language ("fire drill") and escalated the ticket to **Priority: Highest**. |
| **Hierarchical Creation** | *"Marketing wants a frontend... maybe in Streamlit."* | **Success:** Created a new task `KAN-14` and **automatically nested it** under the parent Epic `KAN-13`. |

---

## 📑 Project Management Artifacts

As part of this project, I treated the development process as a formal Agile sprint.

### Product Charter
* **Vision:** To eliminate the "administrative tax" of technical program management.
* **Core Objective:** Deploy a semantic analysis tool that reduces ticket entry time by 90%.

### Retrospective (Implemented Features)
* ✅ **Semantic Duplicate Detection:** Prevents board clutter.
* ✅ **Secure Authentication:** Uses `.env` for API key management.
* ✅ **Agile Hierarchy:** Enforces Epic/Task parent-child relationships automatically.

---

