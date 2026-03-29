# VisualStats Platform - Quick Start Guide

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone/Download the repository**
   ```bash
   cd LLMViz-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create or update `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   openai_api_base=https://api.openai.com
   ```

### Running the App

```bash
python -m streamlit run app.py
```

The app will open at `http://localhost:8501`

## Features

### 1. **Home Page**
- Overview of the VisualStats platform
- Quick navigation to main features
- Information about capabilities

### 2. **Viz Generator**
- Upload CSV, Excel, JSON, XML, or TXT files
- Describe what visualization you want
- AI automatically generates appropriate charts
- Refine visualizations with custom instructions
- Supported chart types:
  - Bar charts
  - Scatter plots
  - Line graphs
  - Histograms
  - And more!

### 3. **Viz Evaluator**
- Upload existing visualizations (PNG, JPG)
- AI evaluates chart quality
- Provides actionable feedback on:
  - Label visibility
  - Color accessibility
  - Font readability
  - Legends and alignment
  - Overall effectiveness

### 4. **Analytics Dashboard** ⭐ NEW
- View platform-wide statistics
- Track user engagement
- Analyze chart type popularity
- Session metrics
- User interaction patterns

## Database System

The platform now tracks all user interactions in a local SQLite database (`visualstats.db`).

### What Gets Tracked:

- **Datasets uploaded** - What files users upload
- **Queries submitted** - What questions users ask AI
- **Visualizations generated** - What charts are created
- **AI conversations** - Full chat history with LLM
- **Chart refinements** - How users modify charts
- **Session analytics** - Duration, activity counts
- **Clickstream data** - Button clicks and navigation

### Anonymous User IDs

Users are assigned random anonymous names like:
- curious_otter
- smart_squirrel
- brave_fox

This ensures **complete privacy** while enabling research.

### Access Analytics

Click "**Analytics Dashboard**" from the sidebar to view:
- Total users, visualizations, and datasets
- Top chart types used
- Most common user actions
- Average session duration

## Example Workflow

### Using the Visualization Generator

1. Click "**Viz Generator**" from sidebar
2. Upload a CSV file (e.g., sales_data.csv)
3. Read the data overview
4. Ask a question in natural language:
   - "Show sales by region"
   - "What's the trend over time?"
   - "Compare product performance"
5. Select preferred chart type from suggestions
6. View the generated visualization
7. (Optional) Add refinements:
   - "Add a title: Monthly Sales"
   - "Rotate x-axis labels"
   - "Use a different color scheme"

### Using the Visualization Evaluator

1. Click "**Viz Evaluator**" from sidebar
2. Upload an image of a visualization (PNG/JPG)
3. Click "Evaluate Visualization"
4. Receive AI feedback on:
   - Label clarity and visibility
   - Color choices and accessibility
   - Overall design quality
   - Specific improvement suggestions

## Database Files

| File | Purpose |
|------|---------|
| `database.py` | Database module with all data operations |
| `visualstats.db` | Local SQLite database (created automatically) |
| `DATABASE.md` | Complete database documentation |
| `QUICKSTART.md` | This file |

## Tips & Best Practices

### For Best Results:

1. **Clear Question Phrasing**
   - ✅ Good: "Show average sales by product category"
   - ❌ Bad: "interesting stuff"

2. **Appropriate Data Types**
   - Clean datasets work best
   - Ensure consistent formatting
   - Remove empty rows/columns if possible

3. **Chart Type Selection**
   - Bar charts: Comparing categories
   - Line charts: Showing trends over time
   - Scatter plots: Finding correlations
   - Histograms: Distribution analysis

4. **Chart Refinements**
   - Be specific in instructions
   - One improvement at a time works better
   - Use natural language

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| API key error | Check .env file has valid OpenAI API key |
| File won't upload | Try converting to CSV first |
| Chart won't generate | Rephrase your question more clearly |
| DB errors | Delete visualstats.db and restart app |

## Research & Analytics

The database enables research into:

- **Learning patterns**: How students learn visualization
- **Engagement metrics**: User interaction frequency
- **Chart preferences**: Most/least used visualization types
- **Error analysis**: Common failures and recovery patterns
- **AI effectiveness**: Quality of AI suggestions

### Exporting Data for Research

The database can be queried directly:

```python
from database import get_db

db = get_db()

# Get overall statistics
stats = db.get_dashboard_stats()
print(stats)

# Get user interactions
interactions = db.get_user_interactions(user_id="some_user")
```

## Support & Documentation

- **Full Database Docs**: See `DATABASE.md`
- **Source Code**: Check `app.py` and `database.py`
- **Issues**: Check error messages in terminal

## Technology Stack

- **Backend**: Python, Streamlit
- **AI/LLM**: OpenAI GPT-4o, LIDA
- **Database**: SQLite3
- **Visualization**: Seaborn, Plotly, Matplotlib
- **Data Processing**: Pandas, NumPy

## Security & Privacy

- **No personal data** stored (anonymous IDs only)
- **Local database** (not sent to servers)
- **Anonymous tracking** (e.g., "curious_otter" instead of real names)
- **No login required** (suitable for classrooms)

## Next Steps

1. Try uploading a sample dataset
2. Ask a natural language question
3. View generated visualization
4. Refine the chart
5. Check Analytics Dashboard to see your data tracked

---

**Ready to visualize?** 🚀

Launch the app and start exploring your data!

```bash
python -m streamlit run app.py
```

**Happy analyzing!** 📊
