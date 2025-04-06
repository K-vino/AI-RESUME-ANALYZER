# agents/interview_scheduler.py

import datetime
from typing import Optional, Dict, Any

class InterviewScheduler:
    def __init__(self, candidate_name: str):
        self.candidate_name = candidate_name

    def generate_interview_slots(self, start_date: datetime.datetime, days_ahead: int = 7) -> list:
        """Generate available interview slots for the next week"""
        slots = []
        current_date = start_date
        
        # Generate slots for the next week
        for _ in range(days_ahead):
            # Morning slots (9 AM to 12 PM)
            for hour in range(9, 12):
                slot = current_date.replace(hour=hour, minute=0)
                slots.append(slot)
            
            # Afternoon slots (2 PM to 5 PM)
            for hour in range(14, 17):
                slot = current_date.replace(hour=hour, minute=0)
                slots.append(slot)
            
            current_date += datetime.timedelta(days=1)
        
        return slots

    def generate_invite(self, 
                       job_title: str,
                       interview_date: datetime.datetime,
                       interviewer: str,
                       meeting_link: Optional[str] = None,
                       additional_notes: Optional[str] = None) -> Dict[str, Any]:
        """Generate a professional interview invitation"""
        
        # Format the date and time
        formatted_date = interview_date.strftime("%A, %B %d, %Y")
        formatted_time = interview_date.strftime("%I:%M %p")
        
        # Generate the invitation message
        message = f"""
Dear {self.candidate_name},

Thank you for your interest in the {job_title} position. We are pleased to invite you for an interview.

Interview Details:
- Date: {formatted_date}
- Time: {formatted_time}
- Interviewer: {interviewer}
{f'- Meeting Link: {meeting_link}' if meeting_link else ''}

{f'Additional Notes: {additional_notes}' if additional_notes else ''}

Please confirm your availability for this interview slot. If this time doesn't work for you, please let us know your preferred time slots.

Best regards,
{interviewer}
"""
        
        return {
            "candidate_name": self.candidate_name,
            "job_title": job_title,
            "interview_date": interview_date,
            "interviewer": interviewer,
            "meeting_link": meeting_link,
            "additional_notes": additional_notes,
            "message": message.strip(),
            "status": "pending"
        }

    def generate_follow_up(self, 
                         interview_date: datetime.datetime,
                         interviewer: str,
                         feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate a follow-up message after the interview"""
        
        message = f"""
Dear {self.candidate_name},

Thank you for taking the time to interview with us for the position. We appreciate your interest in joining our team.

{f'Interview Feedback: {feedback}' if feedback else 'We will review your interview and get back to you soon with next steps.'}

If you have any questions in the meantime, please don't hesitate to reach out.

Best regards,
{interviewer}
"""
        
        return {
            "candidate_name": self.candidate_name,
            "interview_date": interview_date,
            "interviewer": interviewer,
            "feedback": feedback,
            "message": message.strip(),
            "status": "follow_up"
        }
