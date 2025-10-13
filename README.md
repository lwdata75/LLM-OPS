# LLM OPS - Albert School Bootcamp MSC2

This repository contains the coursework and projects for the LLM OPS bootcamp.

## Setup Instructions

### Prerequisites
- Python 3.11.6
- Git
- Docker
- uv package manager

### Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd "LLM OPS"
```

2. Create and activate the virtual environment:
```bash
uv sync
```

This will:
- Create a `.venv` folder with all required dependencies
- Install the following GCP packages:
  - `google-cloud-aiplatform`
  - `google-cloud-bigquery`
  - `google-cloud-storage`

3. Activate the virtual environment:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

4. Verify the setup:
```bash
python --version  # Should show Python 3.11.6
```

### Project Structure

```
.
├── README.md
├── pyproject.toml          # Project dependencies
├── .gitignore              # Git ignore rules
├── .env.example            # Example environment variables (to be created)
├── .env                    # Your environment variables (not tracked in git)
├── session1_practice.md    # Session 1 instructions
└── yoda_sentences.csv      # Dataset
```

### Environment Variables

Create a `.env` file based on `.env.example` with your GCP configuration:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_REGION`: The GCP region (e.g., `us-central1`)
- `GCP_BUCKET_NAME`: Your GCS bucket name

## Team Members
- [Add team member names here]

## Course Information
- **School**: Albert School
- **Program**: Bootcamp MSC2
- **Course**: LLM OPS
