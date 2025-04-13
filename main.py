# main.py

import streamlit as st
import pandas as pd
import PyPDF2  
import json
import os
import re
import datetime
from models.llm_client import LLMClient
from agents.resume_extractor import ResumeExtractor
from agents.jd_summarizer import JobDescriptionSummarizer
from agents.matcher import ResumeJDMatcher
from agents.shortlister import Shortlister
from agents.interview_scheduler import InterviewScheduler
from db.database import ResumeMatchDB

# === Streamlit UI ===
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📋", layout="wide")
st.title("📋 AI Resume Analyzer")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'scheduled_interviews' not in st.session_state:
    st.session_state.scheduled_interviews = []
if 'interview_data' not in st.session_state:
    st.session_state.interview_data = {}
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# === API KEY ===
HF_API_KEY = "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"

# === Upload Resume ===
st.subheader("📂 Upload Resumes")
uploaded_files = st.file_uploader("Upload multiple resumes (PDF)", type=["pdf"], accept_multiple_files=True)

# === Job Description Input ===
st.subheader("📝 Job Description")
jd_input_type = st.radio("Select input method:", ["Text Input", "Upload File"], horizontal=True)
job_descriptions = []

if jd_input_type == "Text Input":
    job_description = st.text_area("Enter job description:", height=200)
    if job_description:
        job_descriptions.append({"title": "Job Description", "content": job_description})

elif jd_input_type == "Upload File":
    jd_file = st.file_uploader("Upload job description file (PDF, TXT, or CSV)", type=["pdf", "txt", "csv"])
    
    if jd_file:
        if jd_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(jd_file)
            content = " ".join(page.extract_text() for page in reader.pages)
            job_descriptions.append({"title": jd_file.name, "content": content})
            
        elif jd_file.type == "text/plain":
            content = jd_file.read().decode("utf-8")
            job_descriptions.append({"title": jd_file.name, "content": content})
            
        elif jd_file.type == "text/csv":
            try:
                encodings = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
                df = None
                
                for encoding in encodings:
                    try:
                        jd_file.seek(0)
                        df = pd.read_csv(jd_file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    st.error("❌ Could not read CSV file with any supported encoding")
                elif 'Job Title' in df.columns and 'Job Description' in df.columns:
                    job_descriptions = [{"title": row['Job Title'], "content": row['Job Description']} 
                                     for _, row in df.iterrows()]
                else:
                    st.error("❌ CSV must contain 'Job Title' and 'Job Description' columns")
            except Exception as e:
                st.error(f"❌ Error reading CSV file: {str(e)}")

# Database status indicator
try:
    db = ResumeMatchDB()
    st.sidebar.success("✅ Database Connected")
except Exception as e:
    st.sidebar.error("❌ Database Connection Error")

# Search functionality
st.sidebar.subheader("🔍 Search Candidates")

# ✅ Initialize session state key if not already present
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# 🔍 Display search input
st.session_state.search_query = st.sidebar.text_input("Search by name or role", st.session_state.search_query)

def format_date(date_str):
    """Format date string for better readability"""
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date.strftime("%B %d, %Y at %I:%M %p")
    except:
        return date_str

def display_statistics():
    """Display basic statistics"""
    if st.session_state.results:
        total_candidates = len(st.session_state.results)
        shortlisted = sum(1 for r in st.session_state.results if r['best_match']['is_shortlisted'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Candidates", total_candidates)
        with col2:
            st.metric("Shortlisted", shortlisted)

def filter_results(results, query):
    """Filter results based on search query"""
    if not query:
        return results
    query = query.lower()
    return [
        r for r in results 
        if query in r['candidate_name'].lower() or 
           query in r['best_match']['job_title'].lower()
    ]

def extract_candidate_info(resume_text):
    """Extract candidate name and email from resume text"""
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    email = re.search(email_pattern, resume_text)
    email = email.group(0) if email else "Not found"
    
    lines = resume_text.split('\n')
    name = "Not found"
    
    name_patterns = [
        r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',
        r'^[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+$',
        r'^[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+$'
    ]
    
    for line in lines:
        line = line.strip()
        if line and '@' not in line:
            for pattern in name_patterns:
                if re.match(pattern, line):
                    name = line
                    break
            if name != "Not found":
                break
                
    return name, email

def analyze_resumes():
    """Analyze resumes and store results in session state"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("Analyzing resumes..."):
        results = []
        total_steps = len(uploaded_files) * len(job_descriptions)
        current_step = 0
        
        db = ResumeMatchDB()
        
        for uploaded_file in uploaded_files:
            status_text.text(f"📄 Processing {uploaded_file.name}...")
            extractor = ResumeExtractor(uploaded_file)
            resume_text = extractor.get_resume_text()
            candidate_name, candidate_email = extract_candidate_info(resume_text)
            
            candidate_id = db.insert_candidate(
                name=candidate_name,
                email=candidate_email,
                resume_path=uploaded_file.name
            )
            
            resume_results = []
            for jd in job_descriptions:
                current_step += 1
                progress = current_step / total_steps
                progress_bar.progress(progress)
                
                status_text.text(f"🔍 Matching with {jd['title']}...")
                jd_agent = JobDescriptionSummarizer(jd['content'])
                jd_summary = jd_agent.get_summary()
                
                llm = LLMClient(api_key=HF_API_KEY)
                matcher = ResumeJDMatcher(llm)
                shortlister = Shortlister(threshold=70.0)
                
                match_result = matcher.match_resume_to_job(resume_text, jd_summary)
                match_percent = shortlister.compute_final_score(match_result)
                is_shortlisted = shortlister.is_shortlisted(match_percent)
                
                job_id = db.insert_job_description(
                    title=jd['title'],
                    description=jd['content']
                )
                
                match_data = {
                    'match_score': match_percent,
                    'skills_match': match_result['skills_match'],
                    'experience_match': match_result['experience_match'],
                    'education_match': match_result['education_match'],
                    'certifications_match': match_result['certifications_match'],
                    'summary': match_result['summary'],
                    'is_shortlisted': is_shortlisted
                }
                db.insert_match_result(candidate_id, job_id, match_data)
                
                resume_results.append({
                    "job_title": jd['title'],
                    "match_score": match_percent,
                    "is_shortlisted": is_shortlisted,
                    "details": match_result,
                    "job_id": job_id
                })
            
            best_match = max(resume_results, key=lambda x: x['match_score'])
            
            results.append({
                "candidate_name": candidate_name,
                "candidate_email": candidate_email,
                "resume_name": uploaded_file.name,
                "best_match": best_match,
                "candidate_id": candidate_id
            })
        
        progress_bar.empty()
        status_text.empty()
        st.session_state.results = results

def display_results():
    """Display analysis results and handle interview scheduling"""
    if not st.session_state.results:
        return
    
    # Display statistics
    display_statistics()
    
    st.subheader("🎯 Analysis Results")
    
    # Filter results based on search
    filtered_results = filter_results(st.session_state.results, st.session_state.search_query)
    
    # Create a list to store all candidates for download
    all_candidates = []
    
    for result in filtered_results:
        with st.expander(f"📄 {result['candidate_name']} ({result['candidate_email']})"):
            st.write(f"**Resume:** {result['resume_name']}")
            
            match = result['best_match']
            st.subheader(f"Best Match: {match['job_title']}")
            st.metric("Match Score", f"{match['match_score']:.1f}%")
            
            all_candidates.append({
                "Name": result['candidate_name'],
                "Email": result['candidate_email'],
                "Resume": result['resume_name'],
                "Best Match Role": match['job_title'],
                "Match Score": f"{match['match_score']:.1f}%",
                "Status": "Shortlisted" if match['is_shortlisted'] else "Not Shortlisted"
            })
            
            if match['is_shortlisted']:
                st.success("✅ Shortlisted")
                handle_interview_scheduling(result, match)
            else:
                st.warning("⚠️ Not Shortlisted")
            
            display_match_details(match['details'])
    
    # Add download button for candidate list
    if all_candidates:
        df_candidates = pd.DataFrame(all_candidates)
        csv = df_candidates.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Candidate List",
            data=csv,
            file_name="candidate_list.csv",
            mime="text/csv"
        )

def handle_interview_scheduling(result, match):
    """Handle interview scheduling for a candidate"""
    st.subheader("📅 Schedule Interview")
    
    interview_key = f"interview_{result['candidate_id']}"
    if interview_key not in st.session_state.interview_data:
        st.session_state.interview_data[interview_key] = {
            "interviewer": "",
            "meeting_link": "",
            "notes": "",
            "selected_slot": None
        }
    
    data = st.session_state.interview_data[interview_key]
    
    data["interviewer"] = st.text_input(
        "Interviewer Name",
        value=data["interviewer"],
        key=f"interviewer_{result['candidate_id']}"
    )
    
    data["meeting_link"] = st.text_input(
        "Meeting Link (optional)",
        value=data["meeting_link"],
        key=f"meeting_{result['candidate_id']}"
    )
    
    data["notes"] = st.text_area(
        "Additional Notes",
        value=data["notes"],
        key=f"notes_{result['candidate_id']}"
    )
    
    scheduler = InterviewScheduler(result['candidate_name'])
    start_date = datetime.datetime.now() + datetime.timedelta(days=1)
    slots = scheduler.generate_interview_slots(start_date)
    
    data["selected_slot"] = st.selectbox(
        "Select Interview Slot",
        options=slots,
        format_func=lambda x: x.strftime("%A, %B %d, %Y at %I:%M %p"),
        key=f"slot_{result['candidate_id']}",
        index=slots.index(data["selected_slot"]) if data["selected_slot"] in slots else 0
    )
    
    if st.button("Schedule Interview", key=f"schedule_{result['candidate_id']}"):
        if data["selected_slot"] and data["interviewer"]:
            schedule_interview(result, match, data)
        else:
            st.error("Please provide interviewer name and select a time slot")

def schedule_interview(result, match, data):
    """Schedule an interview and update session state"""
    db = ResumeMatchDB()
    scheduler = InterviewScheduler(result['candidate_name'])
    
    invite = scheduler.generate_invite(
        job_title=match['job_title'],
        interview_date=data["selected_slot"],
        interviewer=data["interviewer"],
        meeting_link=data["meeting_link"],
        additional_notes=data["notes"]
    )
    
    db.schedule_interview(
        candidate_id=result['candidate_id'],
        job_id=match['job_id'],
        scheduled_date=data["selected_slot"],
        interviewer=data["interviewer"],
        meeting_link=data["meeting_link"],
        notes=data["notes"]
    )
    
    st.session_state.scheduled_interviews.append({
        "candidate_id": result['candidate_id'],
        "candidate_name": result['candidate_name'],
        "job_title": match['job_title'],
        "interview_date": data["selected_slot"],
        "interviewer": data["interviewer"]
    })
    
    st.success("✅ Interview Scheduled!")
    st.write("**Interview Invitation:**")
    st.write(invite['message'])

def display_match_details(details):
    """Display match details in a clean format"""
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Skills Match", f"{details['skills_match']}%")
        st.metric("Experience Match", f"{details['experience_match']}%")
    with col2:
        st.metric("Education Match", f"{details['education_match']}%")
        st.metric("Certifications Match", f"{details['certifications_match']}%")
    
    st.write("**Summary:**")
    st.write(details['summary'])

def display_scheduled_interviews():
    """Display scheduled interviews and handle feedback"""
    st.subheader("📅 Upcoming Interviews")
    db = ResumeMatchDB()
    interviews = db.get_scheduled_interviews(status='pending')
    
    if interviews:
        for interview in interviews:
            with st.expander(f"Interview with {interview['candidate_name']} for {interview['job_title']}"):
                st.write(f"**Date:** {format_date(interview['scheduled_date'])}")
                st.write(f"**Interviewer:** {interview['interviewer']}")
                if interview['meeting_link']:
                    st.write(f"**Meeting Link:** {interview['meeting_link']}")
                if interview['notes']:
                    st.write(f"**Notes:** {interview['notes']}")
                
                feedback = st.text_area("Interview Feedback", key=f"feedback_{interview['id']}")
                if st.button("Submit Feedback", key=f"submit_{interview['id']}"):
                    if feedback:
                        db.update_interview_status(
                            interview_id=interview['id'],
                            status='completed',
                            notes=feedback
                        )
                        st.success("✅ Feedback submitted!")
                    else:
                        st.error("Please provide feedback")
    else:
        st.info("No upcoming interviews scheduled.")

# Main execution
if uploaded_files and job_descriptions:
    if st.button("🔍 Analyze Resumes"):
        analyze_resumes()

if st.session_state.results:
    display_results()
    display_scheduled_interviews()
