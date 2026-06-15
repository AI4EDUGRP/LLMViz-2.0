# VisualStats Platform - Database Documentation

## Overview

The VisualStats platform now includes a comprehensive database system to track user interactions, AI conversations, and platform analytics. This allows instructors and researchers to understand how students interact with the visualization system.

## Database Architecture

### Technology Stack

- **Database**: SQLite (default for local development)
- **Python Module**: `database.py`
- **Integration**: Directly embedded in Streamlit app

### Database Schema

The platform uses 7 main tables:

#### 1. **Users Table**
Stores anonymous user sessions.

```sql
users
- user_id (TEXT, PRIMARY KEY)
- session_id (TEXT, UNIQUE)
- created_at (TIMESTAMP)
- device_type (TEXT)
- last_active (TIMESTAMP)
- anonymous_name (TEXT) -- e.g., "curious_otter", "smart_squirrel"
```

#### 2. **Interactions Table**
Logs all user actions (uploads, clicks, queries, chart refinements).

```sql
interactions
- interaction_id (TEXT, PRIMARY KEY)
- user_id (TEXT, FOREIGN KEY)
- timestamp (TIMESTAMP)
- action_type (TEXT) -- e.g., "dataset_upload", "query_submitted", "chart_refined"
- action_details (TEXT/JSON)
- page_section (TEXT) -- Which section of app: "Viz Generator", "Viz Evaluator", etc.
```

**Action Types Tracked:**
- `dataset_upload` - User uploads a CSV/Excel/JSON file
- `query_submitted` - User asks a visualization question
- `chart_refined` - User refines a generated chart
- `visualization_evaluated` - User evaluates a visualization

#### 3. **AI Conversations Table**
Tracks all interactions with the AI system (GPT-4o).

```sql
ai_conversations
- conversation_id (TEXT, PRIMARY KEY)
- user_id (TEXT, FOREIGN KEY)
- timestamp (TIMESTAMP)
- user_query (TEXT) -- Original user question
- ai_response (TEXT) -- Full AI response
- visualization_generated (BOOLEAN)
- chart_type (TEXT) -- Type of chart generated (bar, scatter, etc.)
- model_used (TEXT)
```

#### 4. **Datasets Table**
Stores metadata about uploaded datasets.

```sql
datasets
- dataset_id (TEXT, PRIMARY KEY)
- user_id (TEXT, FOREIGN KEY)
- upload_time (TIMESTAMP)
- dataset_name (TEXT)
- file_type (TEXT) -- csv, xlsx, json, xml, txt
- file_size_bytes (INTEGER)
- num_rows (INTEGER)
- num_columns (INTEGER)
- column_names (TEXT/JSON) -- JSON array of column names
```

#### 5. **Visualizations Table**
Logs all generated visualizations.

```sql
visualizations
- viz_id (TEXT, PRIMARY KEY)
- dataset_id (TEXT, FOREIGN KEY)
- user_id (TEXT, FOREIGN KEY)
- viz_type (TEXT) -- bar, scatter, line, histogram, etc.
- columns_used (TEXT/JSON) -- Which columns were used
- generated_at (TIMESTAMP)
- user_query (TEXT) -- The original question that led to this viz
- validation_status (TEXT) -- generated, evaluated, validated
- feedback (TEXT) -- User or AI feedback
```

#### 6. **Clickstream Table**
Tracks individual button clicks and UI interactions.

```sql
clickstream
- click_id (TEXT, PRIMARY KEY)
- user_id (TEXT, FOREIGN KEY)
- timestamp (TIMESTAMP)
- element_type (TEXT) -- button, menu, input, etc.
- element_name (TEXT) -- "Generate Chart", "Upload Dataset", etc.
- page_url (TEXT) -- Current page/section
- session_id (TEXT) -- Sessionid for correlating clicks
```

#### 7. **Sessions Table**
Tracks overall session statistics.

```sql
sessions
- session_id (TEXT, PRIMARY KEY)
- user_id (TEXT, FOREIGN KEY)
- start_time (TIMESTAMP)
- end_time (TIMESTAMP)
- duration_seconds (INTEGER)
- datasets_uploaded (INTEGER)
- visualizations_created (INTEGER)
- queries_made (INTEGER)
```

## Key Features

### 1. Anonymous User Tracking

Users are assigned random IDs and anonymous names like:
- `curious_otter`
- `smart_squirrel`
- `brave_fox`

This protects student privacy while enabling analytics.

### 2. Automatic Data Collection

The platform automatically logs:

- **File uploads** - When, what type, file size
- **User queries** - Exact questions asked
- **Chart generation** - Types created, columns used
- **AI interactions** - Every conversation with LLM
- **Chart refinements** - How users modify charts
- **Evaluation feedback** - Quality assessment results
- **Session metrics** - Duration, activity counts

### 3. Analytics Dashboard

Access the **Analytics Dashboard** from the sidebar menu to view:

- **Total Users** - Number of active users
- **Total Visualizations** - Charts generated across platform
- **Total Datasets** - Files uploaded
- **Total Interactions** - All trackable user actions
- **Top Chart Types** - Most frequently used visualization types
- **Session Duration** - Average time spent per session
- **Top Actions** - Most common user behaviors

## API Usage

### Basic Database Operations

```python
from database import get_db

# Get database instance
db = get_db()

# Log an interaction
db.log_interaction(
    user_id="user123",
    action_type="query_submitted",
    action_details={"query": "Show sales by region"},
    page_section="Viz Generator"
)

# Log an AI conversation
db.log_ai_conversation(
    user_id="user123",
    user_query="What is the trend?",
    ai_response="The data shows...",
    visualization_generated=True,
    chart_type="line"
)

# Log dataset upload
db.log_dataset_upload(
    user_id="user123",
    dataset_name="sales_data.csv",
    file_type="csv",
    file_size=45000,
    num_rows=1000,
    num_columns=5,
    column_names=["Date", "Sales", "Region", "Product", "Quantity"]
)

# Log visualization creation
db.log_visualization(
    user_id="user123",
    dataset_id="dataset456",
    viz_type="bar",
    columns_used=["Region", "Sales"],
    user_query="Show sales by region",
    validation_status="generated"
)

# Get user's recent interactions
interactions = db.get_user_interactions(user_id="user123", limit=50)

# Get platform statistics
stats = db.get_dashboard_stats()
```

## Data Pipeline

### User Journey Tracking

1. **User Enters Platform**
   - New `user_id` created
   - Anonymous name assigned
   - Session initialized

2. **User Uploads Dataset**
   - `datasets` table records metadata
   - `interactions` table logs upload action
   - File analyzed and columns extracted

3. **User Asks Question**
   - Question logged in `interactions`
   - Query sent to AI
   - `ai_conversations` records full exchange

4. **Chart Generated**
   - `visualizations` table records creation
   - Chart type, columns used, and query stored
   - User can refine chart

5. **Chart Refinement**
   - Refinement instructions logged
   - New visualization created
   - All iterations tracked

6. **Session Ends**
   - `sessions` table updated with end time
   - Duration calculated
   - Interaction counts finalized

## Research Use Cases

The database enables research into:

### Learning Patterns
- How do students learn data visualization?
- What types of questions do they ask?
- Which chart types do they prefer?

### Error Analysis
- What queries fail validation?
- How do students recover from errors?
- Which datasets cause problems?

### Student Engagement
- Session duration trends
- Interaction frequency
- Feature adoption rates

### Visualization Understanding
- Most used visualization types
- Correlation between visualization types and data characteristics
- Quality of generated visualizations

### AI Interaction Patterns
- Query complexity over time
- Chart type recommendations accuracy
- User satisfaction with AI suggestions

## Database File

- **Location**: `visualstats.db` (created automatically in app directory)
- **Size**: Typically grows to 1-10 MB with normal usage
- **Format**: SQLite3 (can be opened with DB Browser, Python, etc.)
- **Backup**: Regular backups recommended for research data

## Future Enhancements

### Planned Features

1. **PostgreSQL Migration**
   - For production/research deployments
   - Multi-server support
   - Better concurrency handling

2. **Supabase Integration**
   - Cloud-hosted database
   - Real-time analytics
   - Built-in authentication

3. **Advanced Analytics**
   - User cohort analysis
   - Funnel analysis
   - A/B testing framework

4. **Export Capabilities**
   - Export to CSV for analysis
   - Python/R compatible format
   - Automated reports

5. **Data Privacy**
   - GDPR compliance options
   - Data retention policies
   - Anonymization routines

## Security Considerations

### Current Implementation

- **Anonymity**: No personal data stored (only anonymous IDs)
- **Storage**: Local SQLite (change for production)
- **Access**: No authentication required (suitable for classroom)

### For Production

1. Move to PostgreSQL or Supabase
2. Add user authentication
3. Implement access controls
4. Add data encryption
5. Set up regular backups
6. Implement audit logging

## Troubleshooting

### Database Won't Initialize

```bash
# Delete the old database and restart app
rm visualstats.db
streamlit run app.py
```

### Can't Log Data

Check that `database.py` is in the same directory as `app.py` and required imports are available:

```bash
pip install sqlite3  # Usually pre-installed with Python
```

### Database Getting Too Large

Clean old sessions:

```python
from database import get_db
import sqlite3

db = get_db()
conn = sqlite3.connect("visualstats.db")
cursor = conn.cursor()

# Delete sessions older than 30 days
cursor.execute("""
    DELETE FROM sessions 
    WHERE end_time < datetime('now', '-30 days')
""")
conn.commit()
conn.close()
```

## Support

For questions or issues:
1. Check the database.py source code
2. Review the Analytics Dashboard for data insights
3. Export database for external analysis

---

**Last Updated**: March 2026
**Database Version**: 1.0
