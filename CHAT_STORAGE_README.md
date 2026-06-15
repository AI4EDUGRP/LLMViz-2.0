# Enhanced Chat & Image Storage System

## Overview

The `chat_storage.py` module provides a comprehensive system for storing complete chat histories, generated visualizations, and conversation context for each user session.

## Directory Structure

```
data/
├── chats/
│   └── chat_{user_id}_{session_id}.json      # Complete chat history with all messages
└── images/
    └── {user_id}/{session_id}/
        ├── chart_abc12345.png                 # Generated chart images
        ├── chart_def67890.png
        └── ...
```

## Chat History Format

Each chat session is stored as a JSON file containing:

```json
{
  "user_id": "user_123abc",
  "username": "john_doe",
  "session_id": "session_1234567890",
  "created_at": "2026-03-18T10:30:00.000000",
  "dataset_name": "sales_data.csv",
  "dataset_summary": {
    "columns": [...],
    "data_types": {...}
  },
  "messages": [
    {
      "id": "msg123",
      "timestamp": "2026-03-18T10:30:15.000000",
      "role": "user",
      "content": "Show me the sales by region",
      "metadata": {
        "source": "viz_generator"
      }
    },
    {
      "id": "msg124",
      "timestamp": "2026-03-18T10:30:20.000000",
      "role": "assistant",
      "content": "Creating a bar chart showing sales distribution across regions...",
      "metadata": {
        "response_time_seconds": 5.2,
        "model": "gpt-4o",
        "chart_type": "Bar Chart"
      }
    }
  ],
  "generated_images": [
    {
      "id": "img123",
      "filename": "chart_abc12345.png",
      "path": "/data/images/user_123abc/session_1234567890/chart_abc12345.png",
      "chart_type": "Bar Chart",
      "user_query": "Show me the sales by region",
      "format": "png",
      "file_size_bytes": 145892,
      "created_at": "2026-03-18T10:30:20.000000"
    }
  ],
  "refinements": [
    {
      "id": "ref123",
      "timestamp": "2026-03-18T10:30:45.000000",
      "original_query": "Show me the sales by region",
      "refinement": "Make the chart colors more vibrant",
      "response_time_seconds": 2.1
    }
  ],
  "insights": []
}
```

## API Usage

### Saving Chat Messages

```python
from chat_storage import save_chat_message

# Save a user message
save_chat_message(
    user_id="user_123",
    session_id="session_456",
    role="user",
    content="Show me sales trends",
    metadata={"source": "viz_generator"}
)

# Save an AI response
save_chat_message(
    user_id="user_123",
    session_id="session_456",
    role="assistant",
    content="Generating visualization...",
    metadata={
        "response_time_seconds": 2.5,
        "model": "gpt-4o",
        "chart_type": "Line Chart"
    }
)
```

### Saving Generated Images

```python
from chat_storage import save_generated_image

image_metadata = save_generated_image(
    user_id="user_123",
    session_id="session_456",
    image_data=image_bytes,  # Binary data
    chart_type="Bar Chart",
    query="Show sales by region",
    image_format="png"
)
```

### Retrieving Chat History

```python
from chat_storage import get_chat_history, get_session_images

# Get complete chat history
chat_data = get_chat_history("user_123", "session_456")

# Get all images generated in session
images = get_session_images("user_123", "session_456")

# Get session statistics
stats = get_session_statistics("user_123", "session_456")
# Returns: {
#   "total_messages": 15,
#   "user_messages": 8,
#   "ai_messages": 7,
#   "total_images_generated": 3,
#   "total_refinements": 2,
#   "total_response_time_seconds": 12.4
# }
```

### Exporting Chat Data

```python
from chat_storage import export_chat_to_json

# Export entire chat session
export_chat_to_json("user_123", "session_456", "export_chat.json")
```

### Saving Dataset Summary

```python
from chat_storage import save_dataset_summary

save_dataset_summary(
    user_id="user_123",
    session_id="session_456",
    summary={
        "columns": ["Region", "Sales", "Date"],
        "data_types": {"Region": "string", "Sales": "numeric"},
        "row_count": 1000
    }
)
```

### Saving Refinements

```python
from chat_storage import save_chart_refinement

save_chart_refinement(
    user_id="user_123",
    session_id="session_456",
    original_query="Show sales by region",
    refinement="Increase font size and add gridlines",
    response_time=1.8
)
```

## Data Retrieval for Analytics Dashboard

The analytics dashboard can display:

1. **Chat Timeline**: All messages chronologically
2. **Generated Images**: Gallery of all charts with metadata
3. **Refinement History**: All chart modifications
4. **Performance Metrics**: 
   - Total time spent
   - Response times per query
   - Number of iterations per task

## Benefits

✅ **Complete Audit Trail**: Every interaction is recorded
✅ **Image Archive**: All generated charts are stored with metadata
✅ **Conversation Context**: Full chat history for follow-up analysis
✅ **Performance Tracking**: Response times and processing metrics
✅ **Easy Export**: Sessions can be exported for sharing or archiving
✅ **Scalable Storage**: Organized directory structure for multiple users/sessions

## Storage Considerations

- **Chat Files**: JSON files are compact (~50-500 KB per session typically)
- **Images**: PNG format is used by default (~100-500 KB per image)
- **Cleanup**: Old sessions can be archived or deleted using `cleanup_images()`
- **Backup**: Store data/chats and data/images directories for backup

## Future Enhancements

- [ ] Add search functionality for chat history
- [ ] Implement chat session tagging and filtering
- [ ] Add full-text search across all chats
- [ ] Implement chat session sharing
- [ ] Add chat feedback/ratings system
- [ ] Compress images for storage optimization
- [ ] Add cloud storage integration
