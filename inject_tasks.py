import requests
import time

payloads = [
    {
        "from_email": "pm@company.com",
        "from_name": "Alice Product Manager",
        "subject": "Launch Prep: V2 Alpha",
        "body": "Hey team, we are getting ready for the V2 Alpha launch next week. Bob, you need to configure the staging database by Tuesday. Alice, please finish the UI mockups by Wednesday. Also, Charlie needs to write the release notes by Thursday. Let me know if there are issues.",
        "to_group": "engineering@company.com"
    },
    {
        "from_email": "hr@company.com",
        "from_name": "Dave HR",
        "subject": "Q3 Performance Reviews",
        "body": "Hi everyone, Q3 performance reviews are coming up. All managers must submit their direct reports' evaluations by the 15th. Please schedule your 1-on-1s immediately.",
        "to_group": "managers@company.com"
    }
]

for p in payloads:
    print(f"Sending email: {p['subject']}")
    response = requests.post("http://127.0.0.1:8000/webhook/email", json=p)
    print(f"Response: {response.status_code}")
    time.sleep(2)  # brief pause between webhooks

print("Emails sent successfully. The AI background worker is extracting tasks now!")
