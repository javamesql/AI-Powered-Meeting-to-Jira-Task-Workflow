<div align="center">

  <h1 style="font-size: 2.5rem; font-weight: bold;">
    GenAI Meeting-to-Jira Task Pipeline
  </h1>

  <p style="font-size: 1.2rem; margin-bottom: 20px;">
    <i>A Python automation workflow that ingests meeting audio, understands context via GPT-4o, and executes structured updates to Jira.</i>
  </p>

  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenAI-Whisper_&_GPT4o-green?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Jira-REST_API-0052CC?style=for-the-badge&logo=jira&logoColor=white" alt="Jira">
  <img src="https://img.shields.io/badge/Project_Type-Portfolio_Case_Study-orange?style=for-the-badge" alt="Role">

</div>

---

## 📖 Project Overview

**The Challenge:**
In technical program management, valuable context is often lost between verbal meeting discussions and written Jira tickets. Manually updating backlogs is slow, prone to error, and often results in vague ticket descriptions.

**The Solution:**
I engineered a **"Human-in-the-Loop" AI Pipeline** that transforms unstructured audio files into strict, actionable Jira updates. Unlike basic transcription tools, this project uses an LLM (Large Language Model) as a reasoning engine to:
1.  **Check Context:** Reads the live Jira board first to avoid creating duplicates.
2.  **Infer Priority:** Detects urgency in speech (e.g., "fire drill") to assign priority levels automatically.
3.  **Structure Data:** Formats the output into a JSON payload for the Jira API.

---

## 📸 Workflow & Visuals

### 1. The Process (Terminal Execution)
*The script processing the audio file and establishing a connection with the Jira API.*

<div align="center">
  <img src="assets/terminal_loading.png" width="100%" alt="Terminal Processing">
</div>

<br>

### 2. The "Human Approval" Gate
*Before any data touches the Jira database, the Agent presents a "Proposed Change Plan." I designed this safety layer to prevent AI hallucinations from corrupting project data.*

<div align="center">
  <img src="assets/terminal_approval.png" width="90%" alt="Approval Interface">
</div>

<br>

### 3. Jira Impact (Before vs. After)
*Demonstrating the Agent's ability to update existing tickets and create new ones based on a single meeting.*

| **Before: The Stale Board** | **After: Automated Updates** |
| :---: | :---: |
| *Original state of the tickets.*<br><img src="<img width="1222" height="768" alt="Screenshot 2025-12-29 at 2 24 19 PM" src="https://github.com/user-attachments/assets/95c8d775-95b9-461d-a283-99c1dd86d4a6" />
" width="100%"> | *Tickets moved, commented on, and prioritized.*<br><img src="<img width="1221" height="766" alt="Screenshot 2025-12-29 at 2 22 07 PM" src="https://github.com/user-attachments/assets/f7b40e4c-6ae8-45df-8d9b-61b79396de53" />
" width="100%"> |

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

## 🧠 Engineering Challenge: "Hard Mode" Testing

To prove this tool adds real value, I tested it against a "Hard Mode" script containing vague language and implied tasks.

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

