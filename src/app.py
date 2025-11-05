"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Competitive soccer practices and matches",
        "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["noah@mergington.edu", "liam@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Team practices and inter-school games",
        "schedule": "Tuesdays, Thursdays, 5:00 PM - 7:00 PM",
        "max_participants": 15,
        "participants": ["lucas@mergington.edu", "jack@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting, stagecraft, and school productions",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["mia@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Club": {
        "description": "Drawing, painting, and mixed-media projects",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["ava@mergington.edu", "charlotte@mergington.edu"]
    },
    "Debate Team": {
        "description": "Prepare for and compete in debate tournaments",
        "schedule": "Mondays, Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["ethan@mergington.edu", "harper@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Design, build, and program robots for competitions",
        "schedule": "Tuesdays, Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 16,
        "participants": ["oliver@mergington.edu", "amelia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    # Return a normalized copy of activities where each participant is an object
    def normalize_participant(p):
        if isinstance(p, str):
            local = p.split("@")[0]
            return {"email": p, "first_name": local, "last_name": ""}
        # assume dict-like
        return {
            "email": p.get("email") if isinstance(p, dict) else str(p),
            "first_name": (p.get("first_name") if isinstance(p, dict) else "") or "",
            "last_name": (p.get("last_name") if isinstance(p, dict) else "") or "",
        }

    normalized = {}
    for k, v in activities.items():
        item = v.copy()
        parts = item.get("participants", [])
        item["participants"] = [normalize_participant(pp) for pp in parts]
        normalized[k] = item

    return normalized


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, first_name: str = "", last_name: str = ""):
    """Sign up a student for an activity (capture first and last name)"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # normalize and validate email domain
    if not isinstance(email, str):
        raise HTTPException(status_code=400, detail="Invalid email")

    email = email.strip()
    if "@" not in email or not email.lower().endswith("@mergington.com"):
        raise HTTPException(status_code=400, detail="Email must be a Merginton account ending with @mergington.com")

    # validate names (mandatory)
    if not isinstance(first_name, str) or not first_name.strip():
        raise HTTPException(status_code=400, detail="First name is required")
    if not isinstance(last_name, str) or not last_name.strip():
        raise HTTPException(status_code=400, detail="Last name is required")

    # Prevent duplicate signups (case-insensitive); handle stored strings or objects
    normalized = email.lower()
    existing_emails = []
    for p in activity.get("participants", []):
        if isinstance(p, str):
            existing_emails.append(p.lower())
        elif isinstance(p, dict):
            existing_emails.append((p.get("email") or "").lower())

    if normalized in existing_emails:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student as an object with name
    participant_obj = {"email": email, "first_name": first_name.strip(), "last_name": last_name.strip()}
    activity.setdefault("participants", []).append(participant_obj)
    return {"message": f"Signed up {first_name} {last_name} <{email}> for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student (by email) from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    # Find and remove participant by email (handle string or object entries)
    target_index = None
    for idx, p in enumerate(activity.get("participants", [])):
        if isinstance(p, str) and p.lower() == email.lower():
            target_index = idx
            break
        if isinstance(p, dict) and (p.get("email") or "").lower() == email.lower():
            target_index = idx
            break

    if target_index is None:
        raise HTTPException(status_code=404, detail="Student not registered for this activity")

    removed = activity["participants"].pop(target_index)
    removed_email = removed if isinstance(removed, str) else removed.get("email")
    return {"message": f"Unregistered {removed_email} from {activity_name}"}
