# Bhagavad Gita and Patanjali Yoga Sutras Q&A System

A sophisticated question-answering system that leverages natural language processing and machine learning to provide relevant verses and interpretations from the Bhagavad Gita and Patanjali Yoga Sutras.

## Overview

This system combines traditional information retrieval techniques with modern language models to help users understand and explore the wisdom contained in these ancient texts. It provides contextually relevant verses along with generated summaries in response to user queries.

## Architecture

The system follows a multi-stage pipeline architecture:

1. **Data Ingestion Layer**
   - Loads verses from CSV files containing Bhagavad Gita and Patanjali Yoga Sutras
   - Handles multiple data sources with different schema structures
   - Combines and normalizes data for unified processing

2. **Preprocessing Layer**
   - Text cleaning and normalization
   - TF-IDF vectorization for efficient retrieval
   - Handles missing values and standardizes text formats

3. **Retrieval Engine**
   - Cosine similarity-based verse retrieval
   - Ranks verses by relevance to query
   - Returns top-N most relevant verses

4. **Generation Layer**
   - Uses T5-base model for summary generation
   - Contextualizes verses with respect to user query
   - Produces coherent and relevant summaries

5. **Evaluation System**
   - Weighted scoring mechanism
   - Multiple evaluation criteria
   - Performance monitoring and metrics

## Key Features

- **Cross-Text Search**: Seamlessly searches across both Bhagavad Gita and Patanjali Yoga Sutras
- **Bilingual Support**: Handles both Sanskrit and English text
- **Context-Aware**: Maintains contextual relevance in verse retrieval
- **Scalable Architecture**: Designed to accommodate additional texts and languages
- **Performance Monitoring**: Built-in evaluation metrics and quality assessment

## Technical Stack

- **Python 3.10+**
- **Key Libraries**:
  - transformers (T5 model)
  - scikit-learn (TF-IDF, cosine similarity)
  - pandas (data handling)
  - numpy (numerical operations)
  - torch (deep learning)

 ## Pipeline Flowchart
<img width="1440" alt="Screenshot 2025-01-20 at 12 03 28 PM" src="https://github.com/user-attachments/assets/0550efc7-5417-44b6-823e-a8309afab9ca" />

## Performance Metrics

The system is evaluated based on weighted criteria:
- Accuracy of Retrieved Verse (30%)
- Contextual Relevance (20%)
- Quality of Prompt and Summary (15%)
- Cost Efficiency (10%)
- Depth and Quality of Analysis (10%)
- Scalability (5%)
- User Experience (5%)
- Error Handling (5%)

## Usage

```python
# Initialize the system
tokenizer, model = load_t5_model()
vectorizer, tfidf_matrix = vectorize_texts(data)

# Query example
query = "How to control the mind?"
retrieved_shlokas, scores = retrieve_shlokas(query, vectorizer, tfidf_matrix, data)
summary = generate_summary(query, shlokas_text, tokenizer, model)
```

## Output Format

The system returns results in JSON format:
```json
{
    "query": "user_query",
    "retrieved_shlokas": [
        {
            "Chapter": "number",
            "Text": "verse_text",
            "Sanskrit": "sanskrit_text",
            "Translation": "english_translation",
            "Source": "text_source"
        }
    ],
    "summary": "generated_summary"
}
```

### Evaluation Metrics Performance
- Total Weighted Score: 4.4/5.0
- Key Highlights:
 - Accuracy of Retrieved Verse: 4.0
 - Contextual Relevance: 4.0
 - Quality of Prompt/Summary: 4.5
 - Cost Efficiency: 4.8

### Cost Metrics Results
- Query Cost: $0.00
- Resource Utilization:
 - Model Loading: One-time overhead
 - Vector Operations: Minimal compute
 - Storage: Local embeddings only

## Current Limitations

1. Summary generation needs improvement for more contextual responses
2. Data preprocessing could be enhanced for better handling of edge cases
3. Non-unique column names in DataFrame need resolution
4. Limited error handling for edge cases

## Future Improvements

1. Enhanced summary generation using more sophisticated prompting
2. Improved data preprocessing pipeline
3. Additional language support
4. Integration of more sacred texts
5. Advanced context understanding
6. User feedback integration
7. Performance optimization for larger datasets

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT License](https://choosealicense.com/licenses/mit/)

## Acknowledgments

- Original texts: Bhagavad Gita and Patanjali Yoga Sutras
- Hugging Face for the T5 model
- Kaggle for hosting the datasets
