import os
import pandas as pd
from datetime import datetime
from database import SessionLocal, Email, engine, Base

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def ingest_data():
    csv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset.csv")
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    print(f"Reading dataset from {csv_file}...")
    df = pd.read_csv(csv_file)
    
    db = SessionLocal()
    
    count = 0
    try:
        for index, row in df.iterrows():
            # Check if email already exists
            existing_email = db.query(Email).filter(Email.id == str(row['Email_ID'])).first()
            if existing_email:
                continue
                
            # Parse datetime
            try:
                sent_time = datetime.strptime(str(row['Sent_Timestamp']), "%Y-%m-%d %H:%M")
            except ValueError:
                sent_time = None
                
            email = Email(
                id=str(row['Email_ID']),
                thread_id=str(row['Thread_ID']),
                thread_sequence=int(row['Thread_Sequence']) if not pd.isna(row['Thread_Sequence']) else 0,
                channel_type=str(row['Channel_Type']) if not pd.isna(row['Channel_Type']) else "",
                department=str(row['Department']) if not pd.isna(row['Department']) else "",
                conversation_category=str(row['Conversation_Category']) if not pd.isna(row['Conversation_Category']) else "",
                client_project_topic=str(row['Client_Project_or_Topic']) if not pd.isna(row['Client_Project_or_Topic']) else "",
                thread_title=str(row['Thread_Title']) if not pd.isna(row['Thread_Title']) else "",
                sent_timestamp=sent_time,
                from_name=str(row['From_Name']) if not pd.isna(row['From_Name']) else "",
                from_email=str(row['From_Email']) if not pd.isna(row['From_Email']) else "",
                sender_role=str(row['Sender_Role']) if not pd.isna(row['Sender_Role']) else "",
                to_group=str(row['To_Group']) if not pd.isna(row['To_Group']) else "",
                cc=str(row['CC']) if not pd.isna(row['CC']) else None,
                subject=str(row['Subject']) if not pd.isna(row['Subject']) else "",
                email_body=str(row['Email_Body']) if not pd.isna(row['Email_Body']) else "",
                attachment_name=str(row['Attachment_Name']) if not pd.isna(row['Attachment_Name']) else None,
                priority=str(row['Priority']) if not pd.isna(row['Priority']) else "",
                processed_by_ai=False
            )
            
            db.add(email)
            count += 1
            
        db.commit()
        print(f"Successfully ingested {count} emails into the database.")
    except Exception as e:
        db.rollback()
        print(f"Error during ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_data()
