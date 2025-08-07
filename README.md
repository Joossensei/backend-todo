# Todo API

## Setup

1. Clone the repository
```bash
git clone <your-repo>
cd todo-app/backend
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your actual values
```

5. Run the application
```bash
uvicorn app.main:app --reload
```
```

This approach ensures your repository stays clean, small, and portable across different environments!