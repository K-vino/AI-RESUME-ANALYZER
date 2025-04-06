# AI Resume Analyzer - GFG x Accenture Hackathon Project

An intelligent resume analysis and interview scheduling system developed for the GFG x Accenture Hackathon. This project aims to revolutionize the recruitment process by leveraging AI to streamline candidate screening and interview management.

## 🏆 Hackathon Details
- **Event**: GFG x Accenture Hackathon
- **Track**: AI/ML
- **Problem Statement**: Streamlining Recruitment Process
- **Team**: [Your Team Name]
- **Submission Date**: 06-04-2025

## 🚀 Features

- **Resume Analysis**: Automatically extracts candidate information from resumes
- **Job Description Matching**: Analyzes resumes against job descriptions
- **Smart Shortlisting**: AI-powered candidate shortlisting based on multiple criteria
- **Interview Scheduling**: Automated interview slot generation and scheduling
- **Database Integration**: SQLite database for storing candidate and interview information
- **User-Friendly Interface**: Streamlit-based web interface with search and filtering
- **Export Capabilities**: Download candidate lists and analysis results
- **Interview Management**: Track and manage interviews with feedback system

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite
- **AI/ML**: OpenAI API
- **PDF Processing**: PyPDF2
- **Data Handling**: Pandas, NumPy

## 📋 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## 💻 Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Upload resumes and job descriptions through the web interface
3. View analysis results and shortlisted candidates
4. Schedule interviews and manage the recruitment process

## 📊 Project Structure

```
ai-resume-analyzer/
├── agents/
│   ├── resume_extractor.py
│   ├── jd_summarizer.py
│   ├── matcher.py
│   ├── shortlister.py
│   └── interview_scheduler.py
├── db/
│   └── database.py
├── models/
│   └── llm_client.py
├── main.py
├── requirements.txt
└── README.md
```

## 🗄️ Database Schema

The application uses SQLite with the following tables:
- `candidates`: Stores candidate information
- `job_descriptions`: Stores job descriptions
- `matches`: Stores matching results
- `interviews`: Manages interview scheduling and feedback

## 🎯 Key Innovations

1. **Automated Candidate Information Extraction**: Eliminates manual data entry
2. **Intelligent Matching Algorithm**: Goes beyond keyword matching to understand context
3. **Smart Interview Scheduling**: Automatically generates optimal interview slots
4. **Comprehensive Feedback System**: Tracks interview outcomes and candidate progress
5. **User-Friendly Dashboard**: Provides clear insights and easy navigation

## 🤝 Team Members

- Vino K - Team Leader
- Kavinkumar R - Team Member

## 📝 Future Enhancements

1. Integration with popular ATS systems
2. Advanced analytics dashboard
3. Multi-language support
4. Automated interview question generation
5. Candidate ranking system

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- GeeksforGeeks and Accenture for organizing this hackathon
- Streamlit for the web interface
- SQLite for database management
- OpenAI for AI capabilities
- All open-source contributors whose work made this project possible
