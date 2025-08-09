"""
RAG (Retrieval Augmented Generation) Service for Bhagwad Gita and Patanjali Yoga Sutras
"""

import os
import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

from backend.models.schemas import QueryResponse, Verse, SourceType, SourceInfo, SourcesResponse

class RAGService:
    """
    Service class that handles RAG functionality for spiritual texts
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data: Optional[pd.DataFrame] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.tokenizer = None
        self.model = None
        self.sources_info = {}
        
        # Data directories mapping
        self.data_directories = {
            "gita": data_dir / "BWG data",
            "pys": data_dir / "PYS Data"
        }
        
    async def initialize(self):
        """Initialize the RAG service by loading data and models"""
        print("Initializing RAG Service...")
        
        # Load and preprocess data
        await self._load_datasets()
        await self._preprocess_data()
        await self._vectorize_texts()
        
        # Load T5 model for summarization
        await self._load_t5_model()
        
        print("RAG Service initialization completed successfully!")
    
    async def _load_datasets(self):
        """Load datasets from CSV files"""
        print("Loading datasets...")
        
        def load_and_combine_csv(directory: Path) -> pd.DataFrame:
            combined_df = pd.DataFrame()
            if not directory.exists():
                print(f"Warning: Directory {directory} does not exist")
                return combined_df
                
            for file_path in directory.glob("*.csv"):
                try:
                    df = pd.read_csv(file_path)
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                    print(f"Loaded {len(df)} rows from {file_path.name}")
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
            return combined_df
        
        # Load Gita data - use FULL verse dataset as primary for maximum coverage
        def load_gita_data() -> pd.DataFrame:
            gita_dir = self.data_directories["gita"]
            # Use the MAIN verse dataset as primary (767 verses - complete Bhagavad Gita)
            main_verses_file = gita_dir / "Bhagwad_Gita_Verses_English.csv"
            # Use questions dataset as supplementary for additional context
            questions_file = gita_dir / "Bhagwad_Gita_Verses_English_Questions.csv"
            
            main_df = pd.DataFrame()
            
            # Load main verses dataset first (this has the complete Bhagavad Gita)
            if main_verses_file.exists():
                main_verses_df = pd.read_csv(main_verses_file)
                print(f"Loaded {len(main_verses_df)} MAIN Gita verses from {main_verses_file.name}")
                main_df = main_verses_df.copy()
                
                # Rename columns for consistency
                if 'Chapter' in main_df.columns:
                    main_df['chapter'] = main_df['Chapter']
                if 'Verse' in main_df.columns:
                    main_df['verse'] = main_df['Verse']
                if 'Sanskrit ' in main_df.columns:
                    main_df['sanskrit'] = main_df['Sanskrit ']
                    
                # Use the best available English translation (prioritize Swami Adidevananda)
                if 'Swami Adidevananda' in main_df.columns:
                    main_df['text'] = main_df['Swami Adidevananda'].fillna('')
                elif 'Swami Gambirananda' in main_df.columns:
                    main_df['text'] = main_df['Swami Gambirananda'].fillna('')
                elif 'Swami Sivananda' in main_df.columns:
                    main_df['text'] = main_df['Swami Sivananda'].fillna('')
                elif 'Dr. S. Sankaranarayan' in main_df.columns:
                    main_df['text'] = main_df['Dr. S. Sankaranarayan'].fillna('')
                elif 'Shri Purohit Swami' in main_df.columns:
                    main_df['text'] = main_df['Shri Purohit Swami'].fillna('')
                elif 'English' in main_df.columns:
                    main_df['text'] = main_df['English'].fillna('')
                else:
                    # Fallback to first available text column
                    text_columns = [col for col in main_df.columns if col not in ['Chapter', 'Verse', 'Speaker', 'Sanskrit ']]
                    if text_columns:
                        main_df['text'] = main_df[text_columns[0]].fillna('')
                    else:
                        main_df['text'] = ''
            
            # Load questions dataset and merge for additional context
            if questions_file.exists():
                questions_df = pd.read_csv(questions_file)
                print(f"Loaded {len(questions_df)} Gita questions from {questions_file.name}")
                
                # Only merge if we have the main dataset
                if not main_df.empty:
                    # Merge on chapter and verse to get additional context
                    questions_df['chapter'] = pd.to_numeric(questions_df['chapter'], errors='coerce')
                    questions_df['verse'] = pd.to_numeric(questions_df['verse'], errors='coerce')
                    
                    # Merge to get additional context from questions (only available columns)
                    available_columns = ['chapter', 'verse']
                    if 'concept' in questions_df.columns:
                        available_columns.append('concept')
                    if 'keyword' in questions_df.columns:
                        available_columns.append('keyword')
                    
                    # Only merge if we have additional columns beyond chapter and verse
                    if len(available_columns) > 2:
                        main_df = main_df.merge(
                            questions_df[available_columns], 
                            on=['chapter', 'verse'], 
                            how='left'
                        )
                    
                    # Add concept and keyword columns with default values if they don't exist
                    if 'concept' not in main_df.columns:
                        main_df['concept'] = ''
                    if 'keyword' not in main_df.columns:
                        main_df['keyword'] = ''
                    
                    # Fill missing concepts and keywords
                    main_df['concept'] = main_df['concept'].fillna('')
                    main_df['keyword'] = main_df['keyword'].fillna('')
                
            return main_df
        
        # Load PYS data - use FULL verse dataset for maximum coverage
        def load_pys_data() -> pd.DataFrame:
            pys_dir = self.data_directories["pys"]
            # Use the MAIN verse dataset as primary (311 verses - complete PYS)
            main_verses_file = pys_dir / "Patanjali_Yoga_Sutras_Verses_English.csv"
            # Use questions dataset as supplementary for additional context
            questions_file = pys_dir / "Patanjali_Yoga_Sutras_Verses_English_Questions.csv"
            
            main_df = pd.DataFrame()
            
            # Load main verses dataset first (this has the complete Patanjali Yoga Sutras)
            if main_verses_file.exists():
                main_verses_df = pd.read_csv(main_verses_file)
                print(f"Loaded {len(main_verses_df)} MAIN PYS verses from {main_verses_file.name}")
                main_df = main_verses_df.copy()
                
                # Rename columns for consistency
                if 'Chapter' in main_df.columns:
                    main_df['chapter'] = main_df['Chapter']
                if 'Verse' in main_df.columns:
                    main_df['verse'] = main_df['Verse']
                if 'Sanskrit ' in main_df.columns:  # PYS has "Sanskrit " with space
                    main_df['sanskrit'] = main_df['Sanskrit '].fillna('')
                elif 'Sanskrit' in main_df.columns:
                    main_df['sanskrit'] = main_df['Sanskrit'].fillna('')
                    
                # Use the best available English translation (note: PYS has "Translation " with space)
                if 'English' in main_df.columns:
                    main_df['text'] = main_df['English'].fillna('')
                elif 'Translation ' in main_df.columns:  # PYS has "Translation " with space
                    main_df['text'] = main_df['Translation '].fillna('')
                elif 'translation' in main_df.columns:
                    main_df['text'] = main_df['translation'].fillna('')
                else:
                    # If no specific translation column found, use the first available text column
                    text_columns = [col for col in main_df.columns if col not in ['Chapter', 'Verse', 'Sanskrit', 'Sanskrit ', 'chapter', 'verse', 'sanskrit']]
                    if text_columns:
                        main_df['text'] = main_df[text_columns[0]].fillna('')
                    else:
                        main_df['text'] = ''
            
            # Load questions dataset and merge for additional context
            if questions_file.exists():
                questions_df = pd.read_csv(questions_file)
                print(f"Loaded {len(questions_df)} PYS questions from {questions_file.name}")
                
                # Only merge if we have the main dataset
                if not main_df.empty:
                    # Merge on chapter and verse to get additional context
                    questions_df['chapter'] = pd.to_numeric(questions_df['chapter'], errors='coerce')
                    questions_df['verse'] = pd.to_numeric(questions_df['verse'], errors='coerce')
                    
                    # Merge to get additional context from questions (only available columns)
                    available_columns = ['chapter', 'verse']
                    if 'concept' in questions_df.columns:
                        available_columns.append('concept')
                    if 'keyword' in questions_df.columns:
                        available_columns.append('keyword')
                    
                    # Only merge if we have additional columns beyond chapter and verse
                    if len(available_columns) > 2:
                        main_df = main_df.merge(
                            questions_df[available_columns], 
                            on=['chapter', 'verse'], 
                            how='left'
                        )
                    
                    # Add concept and keyword columns with default values if they don't exist
                    if 'concept' not in main_df.columns:
                        main_df['concept'] = ''
                    if 'keyword' not in main_df.columns:
                        main_df['keyword'] = ''
                    
                    # Fill missing concepts and keywords
                    main_df['concept'] = main_df['concept'].fillna('')
                    main_df['keyword'] = main_df['keyword'].fillna('')
                
            return main_df
        
        # Load both datasets with smarter file selection
        gita_df = load_gita_data()
        pys_df = load_pys_data()
        
        # Store datasets for later use
        self.gita_df = gita_df
        self.pys_df = pys_df
        
        print(f"Loaded {len(gita_df)} Gita verses and {len(pys_df)} PYS verses")
    
    async def _preprocess_data(self):
        """Preprocess and combine the datasets"""
        print("Preprocessing data...")
        
        def find_text_column(df: pd.DataFrame, possible_columns: List[str]) -> str:
            """Find the main text column in the dataframe"""
            for col in possible_columns:
                if col in df.columns and not df[col].isna().all():
                    return col
            # If no specific column found, try to use any column with substantial text
            for col in df.columns:
                if df[col].dtype == 'object' and not df[col].isna().all():
                    sample_text = str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else ""
                    if len(sample_text) > 10:  # Assume meaningful text if longer than 10 chars
                        return col
            raise ValueError(f"No valid text column found in DataFrame. Available columns: {df.columns.tolist()}")
        
        # Preprocess Gita data
        if not self.gita_df.empty:
            # Gita data already has the correct 'text' column from load_gita_data()
            # Just ensure it's properly formatted
            self.gita_df['text'] = self.gita_df['text'].fillna('').astype(str)
            self.gita_df['source'] = 'Gita'
            
            # Handle Sanskrit text - prioritize merged Sanskrit column
            if 'Sanskrit ' in self.gita_df.columns:
                self.gita_df['sanskrit'] = self.gita_df['Sanskrit '].fillna('')
            elif 'sanskrit' in self.gita_df.columns:
                self.gita_df['sanskrit'] = self.gita_df['sanskrit'].fillna('')
            else:
                self.gita_df['sanskrit'] = ''
            
            # Handle chapter and verse - use original columns from questions file
            if 'chapter' in self.gita_df.columns:
                self.gita_df['chapter'] = pd.to_numeric(self.gita_df['chapter'], errors='coerce')
            elif 'Chapter' in self.gita_df.columns:
                self.gita_df['chapter'] = pd.to_numeric(self.gita_df['Chapter'], errors='coerce')
                
            if 'verse' in self.gita_df.columns:
                self.gita_df['verse'] = pd.to_numeric(self.gita_df['verse'], errors='coerce')
            elif 'Verse' in self.gita_df.columns:
                self.gita_df['verse'] = pd.to_numeric(self.gita_df['Verse'], errors='coerce')
            
            # Initialize concept and keyword columns
            if 'concept' not in self.gita_df.columns:
                self.gita_df['concept'] = ''
            else:
                self.gita_df['concept'] = self.gita_df['concept'].fillna('')
                
            if 'keyword' not in self.gita_df.columns:
                self.gita_df['keyword'] = ''
            else:
                self.gita_df['keyword'] = self.gita_df['keyword'].fillna('')
        
        # Preprocess PYS data
        if not self.pys_df.empty:
            # PYS data already has the correct 'text' column from load_pys_data()
            # Just ensure it's properly formatted
            self.pys_df['text'] = self.pys_df['text'].fillna('').astype(str)
            self.pys_df['source'] = 'PYS'
            
            # Try to get Sanskrit column
            sanskrit_cols = ['Sanskrit', 'sanskrit', 'Sanskrit ']
            for col in sanskrit_cols:
                if col in self.pys_df.columns:
                    self.pys_df['sanskrit'] = self.pys_df[col].fillna('')
                    break
            
            # Get chapter and verse numbers
            chapter_cols = ['Chapter', 'chapter']
            for col in chapter_cols:
                if col in self.pys_df.columns:
                    self.pys_df['chapter'] = pd.to_numeric(self.pys_df[col], errors='coerce')
                    break
            
            verse_cols = ['Verse', 'verse']
            for col in verse_cols:
                if col in self.pys_df.columns:
                    self.pys_df['verse'] = pd.to_numeric(self.pys_df[col], errors='coerce')
                    break
                    
            # Initialize concept and keyword columns for PYS
            if 'concept' not in self.pys_df.columns:
                self.pys_df['concept'] = ''
            else:
                self.pys_df['concept'] = self.pys_df['concept'].fillna('')
                
            if 'keyword' not in self.pys_df.columns:
                self.pys_df['keyword'] = ''
            else:
                self.pys_df['keyword'] = self.pys_df['keyword'].fillna('')
        
        # Combine datasets
        self.data = pd.concat([self.gita_df, self.pys_df], ignore_index=True)
        
        # Clean text column
        self.data['text'] = self.data['text'].fillna('').astype(str)
        self.data = self.data[self.data['text'].str.strip() != '']
        
        # Ensure we have required columns
        for col in ['sanskrit', 'translation', 'concept', 'keyword', 'chapter', 'verse']:
            if col not in self.data.columns:
                if col in ['chapter', 'verse']:
                    self.data[col] = None
                else:
                    self.data[col] = ''
        
        # Fill missing values
        self.data = self.data.fillna('')
        
        print(f"Preprocessed {len(self.data)} total verses")
        
        # Store sources info
        self.sources_info = {
            'Gita': {
                'name': 'Bhagavad Gita',
                'total_verses': len(self.gita_df) if not self.gita_df.empty else 0,
                'description': 'A 700-verse Hindu scripture that is part of the epic Mahabharata'
            },
            'PYS': {
                'name': 'Patanjali Yoga Sutras', 
                'total_verses': len(self.pys_df) if not self.pys_df.empty else 0,
                'description': 'A collection of 196 Indian sutras on the theory and practice of yoga'
            }
        }
    
    async def _vectorize_texts(self):
        """Create TF-IDF vectors from the text data"""
        print("Vectorizing texts...")
        
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data available for vectorization")
        
        # Enhanced text extraction for better similarity scores
        texts = []
        for _, row in self.data.iterrows():
            # Combine multiple text sources for richer semantic matching
            primary_text = str(row.get('text', '')).strip()
            translation = str(row.get('translation', '')).strip()
            concept = str(row.get('concept', '')).strip()
            keyword = str(row.get('keyword', '')).strip()
            
            # Create combined text with weighted importance
            combined_parts = []
            if primary_text:
                combined_parts.append(primary_text)
            if translation and translation != primary_text:
                combined_parts.append(translation)
            if concept:
                combined_parts.append(f"{concept}")  # Add concept for semantic relevance
            if keyword:
                combined_parts.append(f"{keyword}")  # Add keywords for better matching
                
            combined_text = " ".join(combined_parts)
            texts.append(combined_text if combined_text.strip() else primary_text)
        
        # Enhanced TF-IDF configuration for better similarity
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=10000,     # Increased vocabulary for better coverage
            ngram_range=(1, 3),     # Include trigrams for better context
            max_df=0.9,            # Less restrictive filtering
            min_df=1,              # Allow single occurrences
            sublinear_tf=True,     # Apply sublinear tf scaling
            norm='l2',             # L2 normalization
            analyzer='word',        # Word-based analysis
            token_pattern=r'(?u)\b\w+\b'  # Unicode-aware word boundaries
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        print(f"Created Enhanced TF-IDF matrix with shape: {self.tfidf_matrix.shape}")
    
    async def _load_t5_model(self):
        """Load T5 model for text summarization"""
        print("Loading T5 model...")
        
        try:
            self.tokenizer = T5Tokenizer.from_pretrained("t5-base", legacy=False)
            self.model = T5ForConditionalGeneration.from_pretrained("t5-base")
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                print("Model moved to GPU")
            
            print("T5 model loaded successfully")
        except Exception as e:
            print(f"Error loading T5 model: {e}")
            self.tokenizer = None
            self.model = None
            
        # Initialize translation support
        self.supported_languages = {
            'hi': 'Hindi',
            'fr': 'French', 
            'de': 'German',
            'es': 'Spanish',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
    
    async def process_query(
        self, 
        query: str, 
        top_n: int = 5, 
        include_summary: bool = True,
        source_filter: Optional[List[SourceType]] = None
    ) -> QueryResponse:
        """
        Process a spiritual query and return relevant verses with optional summary
        """
        start_time = time.time()
        
        # Validate inputs
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        if self.data is None or self.vectorizer is None or self.tfidf_matrix is None:
            raise ValueError("RAG service not properly initialized")
        
        # Filter inappropriate queries
        if not self._is_query_valid(query):
            raise ValueError("Query contains inappropriate content")
        
        # Retrieve relevant verses
        retrieved_verses, similarity_scores = await self._retrieve_verses(
            query, top_n, source_filter
        )
        
        # Generate summary if requested
        summary = None
        if include_summary and len(retrieved_verses) > 0:
            summary = await self._generate_summary(query, retrieved_verses)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return QueryResponse(
            query=query,
            retrieved_verses=retrieved_verses,
            summary=summary,
            total_results=len(retrieved_verses),
            processing_time_ms=round(processing_time, 2)
        )
    
    async def _retrieve_verses(
        self, 
        query: str, 
        top_n: int,
        source_filter: Optional[List[SourceType]] = None
    ) -> Tuple[List[Verse], np.ndarray]:
        """Retrieve the most relevant verses for a query"""
        
        # Enhanced query preprocessing
        query_expanded = query.lower()
        
        # Transform query to vector and calculate proper cosine similarities
        query_vector = self.vectorizer.transform([query_expanded])
        
        # Calculate proper cosine similarity using sklearn's cosine_similarity
        from sklearn.metrics.pairwise import cosine_similarity
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix).ravel()
        
        # Get top N indices with better filtering
        all_indices = cosine_similarities.argsort()[::-1]  # Sort in descending order
        
        # Create verses list
        verses = []
        for idx in all_indices:
            if len(verses) >= top_n:
                break
                
            row = self.data.iloc[idx]
            source = row.get('source', 'Unknown')
            
            # Apply source filter if specified
            if source_filter and source not in source_filter:
                continue
            
            # No threshold filtering - let top_n parameter control results
            
            # Get the best available English translation
            translation = self._get_best_translation(row)
            
            # Get Sanskrit text
            sanskrit_text = self._get_sanskrit_text(row)
            
            # Get Hindi text if available
            hindi_text = self._get_hindi_text(row)
            
            verse = Verse(
                chapter=self._safe_float(row.get('chapter') or row.get('Chapter')),
                verse=self._safe_float(row.get('verse') or row.get('Verse')),
                text=translation or str(row.get('text', '')),
                sanskrit=sanskrit_text,
                translation=translation,
                source=SourceType(source),
                similarity_score=round(float(cosine_similarities[idx]), 4),
                concept=str(row.get('concept', '') or row.get('Concept', '')),
                keyword=str(row.get('keyword', '') or row.get('Keyword', ''))
            )
            verses.append(verse)
        
        return verses, cosine_similarities[all_indices[:len(verses)]]
    
    async def _generate_summary(self, query: str, verses: List[Verse]) -> str:
        """Generate a focused summary of the top 5 retrieved verses - just summarize, don't list individually"""
        
        if not verses:
            return "No relevant verses found for the query."
        
        # Create a focused summary without listing individual verses
        summary_parts = []
        
        # Add query context
        summary_parts.append(f"**Spiritual Insights for '{query}':**")
        
        # Analyze the collective wisdom without listing individual verses
        if len(verses) >= 3:
            summary_parts.append(f"Based on {len(verses)} carefully selected verses from ancient scriptures, the wisdom teachings reveal:")
        else:
            summary_parts.append(f"From the selected spiritual texts:")
        
        # Extract common themes and concepts
        concepts = [v.concept for v in verses if v.concept and v.concept.strip()]
        keywords = [v.keyword for v in verses if v.keyword and v.keyword.strip()]
        
        if concepts:
            unique_concepts = list(set(concepts))[:3]  # Top 3 unique concepts
            summary_parts.append(f"**Key Themes:** {', '.join(unique_concepts)}")
        
        if keywords:
            unique_keywords = list(set(keywords))[:3]  # Top 3 unique keywords
            summary_parts.append(f"**Core Concepts:** {', '.join(unique_keywords)}")
        
        # Add collective wisdom summary
        summary_parts.append(f"\n**Collective Wisdom:** These verses collectively guide us toward understanding {query.lower()} through ancient spiritual teachings, emphasizing the importance of inner discipline, divine connection, and practical application of spiritual principles in daily life.")
        
        return "\n".join(summary_parts)
        
        # Fallback if T5 model is available
        if self.tokenizer and self.model:
            try:
                # Prepare input text for T5
                verses_text = []
                for verse in verses[:3]:
                    if verse.translation and verse.translation.strip():
                        verses_text.append(verse.translation.strip())
                
                if verses_text:
                    combined_text = " ".join(verses_text)
                    prompt = f"summarize: Spiritual teachings about '{query}': {combined_text}"
                    
                    inputs = self.tokenizer(
                        prompt, 
                        return_tensors="pt", 
                        max_length=512, 
                        truncation=True
                    )
                    
                    if torch.cuda.is_available():
                        inputs = {k: v.cuda() for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = self.model.generate(
                            **inputs,
                            max_length=200,
                            min_length=50,
                            num_beams=4,
                            early_stopping=True,
                            no_repeat_ngram_size=2
                        )
                    
                    summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    summary = summary.replace("summarize:", "").strip()
                    
                    if summary:
                        return f"**AI-Generated Insight:** {summary}"
                        
            except Exception as e:
                print(f"Error with T5 generation: {e}")
        
        # Final fallback
        return f"The ancient scriptures offer profound guidance on '{query}' through these {len(verses)} carefully selected verses, each providing unique insights into spiritual growth and understanding."
    
    def _is_query_valid(self, query: str) -> bool:
        """Check if the query is appropriate"""
        inappropriate_keywords = [
            "abuse", "hate", "violence", "illegal", "harmful", 
            "kill", "murder", "suicide", "drugs", "weapon"
        ]
        query_lower = query.lower()
        return not any(keyword in query_lower for keyword in inappropriate_keywords)
    
    def _get_best_translation(self, row) -> str:
        """Get the best available English translation"""
        # Priority order for English translations
        translation_cols = [
            'translation', 'English', 'Swami Adidevananda', 
            'Swami Gambirananda', 'Swami Sivananda', 'text'
        ]
        
        for col in translation_cols:
            if col in row.index:
                text = str(row.get(col, '')).strip()
                if text and len(text) > 10:  # Meaningful content
                    return text
        return ""
    
    def _get_sanskrit_text(self, row) -> str:
        """Get Sanskrit text"""
        sanskrit_cols = ['Sanskrit', 'sanskrit', 'Sanskrit ']
        
        for col in sanskrit_cols:
            if col in row.index:
                text = str(row.get(col, '')).strip()
                if text and len(text) > 5:
                    return text
        return ""
    
    def _get_hindi_text(self, row) -> str:
        """Get Hindi text if available"""
        hindi_cols = ['Hindi', 'hindi', 'Hindi Meaning']
        
        for col in hindi_cols:
            if col in row.index:
                text = str(row.get(col, '')).strip()
                if text and len(text) > 5:
                    return text
        return ""
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    async def get_sources_info(self) -> SourcesResponse:
        """Get information about available text sources"""
        sources = []
        total_verses = 0
        
        for code, info in self.sources_info.items():
            source_info = SourceInfo(
                name=info['name'],
                code=SourceType(code),
                total_verses=info['total_verses'],
                chapters=18 if code == 'Gita' else 4,  # Approximate chapters
                description=info['description']
            )
            sources.append(source_info)
            total_verses += info['total_verses']
        
        return SourcesResponse(
            sources=sources,
            total_verses=total_verses
        )
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """Simple translation using T5 model"""
        if target_language not in self.supported_languages:
            return f"Language '{target_language}' not supported. Available: {list(self.supported_languages.keys())}"
        
        if not self.model or not self.tokenizer:
            return "Translation model not available"
        
        try:
            # Simple translation prompt
            lang_name = self.supported_languages[target_language]
            prompt = f"translate English to {lang_name}: {text}"
            
            # Limit text length for translation
            if len(text) > 200:
                text = text[:200] + "..."
                
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=256, truncation=True)
            
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=150,
                    num_beams=2,
                    early_stopping=True,
                    do_sample=False
                )
            
            translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the output
            if prompt in translation:
                translation = translation.replace(prompt, "").strip()
            
            return translation if translation else "Translation unavailable"
            
        except Exception as e:
            return f"Translation failed: {e}"

