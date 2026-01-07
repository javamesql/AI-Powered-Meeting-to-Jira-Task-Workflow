import os
import json
import sys
from dotenv import load_dotenv
from jira import JIRA
from openai import OpenAI

# --- 1. CONFIGS ---
load_dotenv()
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_SERVER = os.getenv("JIRA_SERVER")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

try:
    jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))
    client = OpenAI(api_key=OPENAI_KEY)
except Exception as e:
    sys.exit(f"Connection Error: {e}")

# --- 2. CONTEXT GATHERING ---
def get_project_context(project_key):
    print(f"\n--- Reading Context from {project_key} ---")
    context = []
    # Fetch active items to check for duplicates
    jql = f'project={project_key} AND issuetype in (Epic, Task) AND status != Done'
    
    try:
        issues = jira.search_issues(jql, maxResults=50)
        for i in issues:
            context.append({
                "key": i.key,
                "summary": i.fields.summary,
                "status": i.fields.status.name,
                "priority": i.fields.priority.name,
                "type": i.fields.issuetype.name
            })
        valid_priorities = [p.name for p in jira.priorities()]
        print(f"   > Found {len(context)} active items.")
        return context, valid_priorities
    except Exception as e:
        print(f"   > Warning: Jira fetch failed ({e})")
        return [], ["Medium"]

def transcribe_audio(audio_path):
    print(f"\n--- Transcribing Audio: {audio_path} ---")
    if not os.path.exists(audio_path):
        sys.exit(f"Error: File '{audio_path}' not found.")
    with open(audio_path, "rb") as f:
        return client.audio.transcriptions.create(model="whisper-1", file=f).text

# --- 3. THE BRAIN ---
def run_jira_agent(transcript, context, valid_priorities):
    print("\n--- Agent: Analyzing Request ---")
    
    system_prompt = f"""
    You are a Senior Technical Program Manager (TPM).
    Analyze the meeting transcript and manage the Jira board.
    
    ### CONTEXT
    1. EXISTING JIRA TICKETS: {json.dumps(context)}
    2. ALLOWED PRIORITY LEVELS: {json.dumps(valid_priorities)}
    
    ### DECISION FRAMEWORK
    
    1. DUPLICATE DETECTION
       - If a request matches the intent of an existing ticket, UPDATE it.
       - NEVER create duplicates.
       
    2. PRIORITY SCORING
       - P1 (Highest): Blockers, security, data loss.
       - P2 (High): Urgent deadlines, broken features.
       - P3 (Medium): Standard tasks.
       - P4 (Low): Typos, nice-to-haves.
    
    3. STATUS LOGIC
       - "In Progress": Currently being worked on.
       - "Done": Finished/Merged.
       
    ### OUTPUT RULES
    - Return valid JSON only.
    - NO Descriptions needed (User will fill these in later).
    
    ### JSON OUTPUT SCHEMA
    {{
      "actions": [
        {{
          "action": "UPDATE",
          "issue_key": "KAN-123", 
          "append_text": "Update: [Summary of new info]",
          "new_priority": "High",
          "new_status": "In Progress"
        }},
        {{
          "action": "CREATE",
          "issuetype": "Task", 
          "summary": "Actionable Title",
          "priority": "Medium"
        }}
      ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"TRANSCRIPT: {transcript}"}
        ]
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        sys.exit(f"AI Error: Returned invalid JSON. {e}")

# --- 4. EXECUTION ---
def execute_changes(plan, project_key, valid_priorities, target_epic_key):
    actions = plan.get("actions", [])
    if not actions:
        print("No actions needed.")
        return

    print("\n" + "="*60)
    print(f"PROPOSED CHANGES FOR {project_key} (Linked to Epic: {target_epic_key})")
    print("="*60)
    
    for i, item in enumerate(actions):
        if item['action'] == "CREATE":
            print(f"[{i+1}] CREATE {item.get('issuetype', 'Task').upper()}")
            print(f"    Summary:  {item['summary']}")
            print(f"    Priority: {item.get('priority', 'Medium')}")
            print(f"    Parent:   {target_epic_key}")
            
        elif item['action'] == "UPDATE":
            print(f"[{i+1}] UPDATE {item['issue_key']}")
            if "append_text" in item:
                print(f"    Note:     {item['append_text'][:60]}...")
            if "new_priority" in item:
                print(f"    Priority: {item['new_priority']}")
            if "new_status" in item:
                print(f"    Status:   {item['new_status']}")
    print("="*60)
    
    if input("\nExecute changes? (y/n): ").lower() != 'y':
        return

    print("\nProcessing...")
    for item in actions:
        try:
            prio = item.get('priority') or item.get('new_priority', 'Medium')
            if prio not in valid_priorities: prio = "Medium" 

            if item["action"] == "CREATE":
                itype = item.get('issuetype', 'Task').capitalize()
                if itype not in ['Epic', 'Task']: itype = 'Task'

                issue_dict = {
                    'project': {'key': project_key},
                    'summary': item['summary'],
                    'issuetype': {'name': itype}, 
                    'priority': {'name': prio},
                    # THIS LINKS THE TASK TO THE EPIC
                    'parent': {'key': target_epic_key} 
                }
                
                # Note: 'parent' field works for standard Jira Cloud. 
                # If using an older on-prem version, you might need "customfield_XXXXX": target_epic_key
                new_issue = jira.create_issue(fields=issue_dict)
                print(f"   [OK] Created {new_issue.key} under {target_epic_key}")

            elif item["action"] == "UPDATE":
                issue = jira.issue(item["issue_key"])
                
                if "new_priority" in item:
                    issue.update(fields={"priority": {"name": prio}})
                    print(f"   [OK] Priority updated to {prio}")

                if "append_text" in item:
                    jira.add_comment(issue, item["append_text"])
                    print(f"   [OK] Comment added")

                if "new_status" in item:
                    target = item["new_status"]
                    transitions = jira.transitions(issue)
                    t_id = next((t['id'] for t in transitions if t['name'].lower() == target.lower()), None)
                    if t_id:
                        jira.transition_issue(issue, t_id)
                        print(f"   [OK] Moved to '{target}'")
                    else:
                        print(f"   [FAIL] Cannot move to '{target}'. Valid moves: {[t['name'] for t in transitions]}")

        except Exception as e:
            print(f"   [FAIL] Error: {e}")

# --- MAIN ---
if __name__ == "__main__":
    PROJECT_KEY = "KAN"
    TARGET_EPIC_KEY = "KAN-13"  # <--- ENTER YOUR EPIC KEY HERE
    AUDIO_FILE = "MicrosoftTeams-video.mp4" 

    context, valid_priorities = get_project_context(PROJECT_KEY)
    transcript = transcribe_audio(AUDIO_FILE)
    plan = run_jira_agent(transcript, context, valid_priorities)
    
    # Pass the Epic Key to the execution function
    execute_changes(plan, PROJECT_KEY, valid_priorities, TARGET_EPIC_KEY)
