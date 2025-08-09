"""
Enhanced RAG (Retrieval Augmented Generation) Service 
for Bhagwad Gita and Patanjali Yoga Sutras with improved similarity and modern models
"""

import os
import json
import time
import asyncio
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import (
    T5Tokenizer, T5ForConditionalGeneration,
    BartTokenizer, BartForConditionalGeneration,
    AutoTokenizer, AutoModelForSeq2SeqLM
)
import torch

from backend.models.schemas import QueryResponse, Verse, SourceType, SourceInfo, SourcesResponse

class EnhancedRAGService:
    """
    Enhanced RAG Service with improved similarity scoring and modern AI models
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        
        # Enhanced data structures
        self.gita_data: Optional[pd.DataFrame] = None
        self.pys_data: Optional[pd.DataFrame] = None
        self.combined_data: Optional[pd.DataFrame] = None
        
        # Multiple vectorizers for better performance
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.semantic_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.semantic_matrix = None
        
        # Modern AI models
        self.summary_tokenizer = None
        self.summary_model = None
        self.translation_tokenizer = None
        self.translation_model = None
        
        # Enhanced sources info
        self.sources_info = {}
        self.gita_df = pd.DataFrame()
        self.pys_df = pd.DataFrame()
        
        # Supported languages for translation
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
    
    async def initialize(self):
        """Initialize the enhanced RAG service"""
        try:
            print("🚀 Initializing Enhanced RAG Service...")
            await self._load_enhanced_data()
            await self._create_enhanced_vectorization()
            await self._load_modern_models()
            print("✅ Enhanced RAG Service initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize enhanced RAG service: {e}")
            return False
    
    async def _load_enhanced_data(self):
        """Load and enhance data from all available sources"""
        print("📚 Loading enhanced datasets...")
        
        # Load Bhagavad Gita with comprehensive data combination
        gita_files = {
            'verses': 'Bhagwad_Gita_Verses_English.csv',
            'concepts': 'Bhagwad_Gita_Verses_Concepts.csv', 
            'questions': 'Bhagwad_Gita_Verses_English_Questions.csv'
        }
        
        gita_data = {}
        gita_path = self.data_dir / "BWG data"
        
        for key, filename in gita_files.items():
            file_path = gita_path / filename
            if file_path.exists():
                df = pd.read_csv(file_path)
                gita_data[key] = df
                print(f"  ✓ Loaded {filename}: {len(df)} rows")
        
        # Create enhanced Gita dataset
        if 'verses' in gita_data:
            gita_base = gita_data['verses'].copy()
            # Standardize column names
            gita_base = gita_base.rename(columns={
                'Sanskrit ': 'sanskrit',
                'Chapter': 'chapter', 
                'Verse': 'verse'
            })
            
            # Merge with concepts if available
            if 'concepts' in gita_data:
                concepts_df = gita_data['concepts'].rename(columns={
                    'Chapter': 'chapter',
                    'Verse': 'verse',
                    'Sanskrit': 'sanskrit_concept',
                    'English': 'english_concept'
                })
                gita_base = gita_base.merge(
                    concepts_df[['chapter', 'verse', 'Concept', 'Keyword', 'sanskrit_concept', 'english_concept']], 
                    on=['chapter', 'verse'], 
                    how='left'
                )
            
            # Add primary translation (best available)
            gita_base['translation'] = gita_base.apply(self._get_best_gita_translation, axis=1)
            gita_base['text'] = gita_base['translation']  # Primary text for search
            gita_base['source'] = 'Gita'
            
            self.gita_data = gita_base
            self.gita_df = gita_base
        
        # Load Patanjali Yoga Sutras
        pys_files = {
            'verses': 'Patanjali_Yoga_Sutras_Verses_English.csv',
            'questions': 'Patanjali_Yoga_Sutras_Verses_English_Questions.csv'
        }
        
        pys_data = {}
        pys_path = self.data_dir / "PYS Data"
        
        for key, filename in pys_files.items():
            file_path = pys_path / filename
            if file_path.exists():
                df = pd.read_csv(file_path)
                pys_data[key] = df
                print(f"  ✓ Loaded {filename}: {len(df)} rows")
        
        # Create enhanced PYS dataset
        if 'verses' in pys_data:
            pys_base = pys_data['verses'].copy()
            # Standardize column names
            pys_base = pys_base.rename(columns={
                'Sanskrit ': 'sanskrit',
                'Translation ': 'translation',
                'Chapter': 'chapter',
                'Verse': 'verse'
            })
            pys_base['text'] = pys_base['translation']  # Primary text for search
            pys_base['source'] = 'PYS'
            
            self.pys_data = pys_base
            self.pys_df = pys_base
        
        # Combine datasets with enhanced features
        combined_data = []
        
        if self.gita_data is not None:
            combined_data.append(self.gita_data)
        if self.pys_data is not None:
            combined_data.append(self.pys_data)
        
        if combined_data:
            self.combined_data = pd.concat(combined_data, ignore_index=True, sort=False)
            
            # Fill missing values intelligently
            self.combined_data = self.combined_data.fillna('')
            
            # Ensure consistent data types
            for col in ['chapter', 'verse']:
                if col in self.combined_data.columns:
                    self.combined_data[col] = pd.to_numeric(self.combined_data[col], errors='coerce')
            
            print(f"📊 Combined dataset: {len(self.combined_data)} total verses")
            
            # Update sources info
            self.sources_info = {
                'Gita': {
                    'name': 'Bhagavad Gita',
                    'total_verses': len(self.gita_df) if not self.gita_df.empty else 0,
                    'chapters': int(self.gita_df['chapter'].max()) if not self.gita_df.empty else 18,
                    'description': 'A 700-verse Hindu scripture that is part of the epic Mahabharata'
                },
                'PYS': {
                    'name': 'Patanjali Yoga Sutras',
                    'total_verses': len(self.pys_df) if not self.pys_df.empty else 0,
                    'chapters': int(self.pys_df['chapter'].max()) if not self.pys_df.empty else 4,
                    'description': 'A collection of 196 Indian sutras on the theory and practice of yoga'
                }
            }
        else:
            raise ValueError("No valid data files found")
    
    def _get_best_gita_translation(self, row):
        """Get the best available English translation for Gita verses"""
        # Priority order for translations
        translation_cols = [
            'Swami Adidevananda',
            'Swami Gambirananda', 
            'Swami Sivananda',
            'Dr. S. Sankaranarayan',
            'Shri Purohit Swami',
            'english_concept'
        ]
        
        for col in translation_cols:
            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                return str(row[col]).strip()
        
        return ""
    
    async def _create_enhanced_vectorization(self):
        """Create enhanced TF-IDF vectorization with multiple strategies"""
        print("🔍 Creating enhanced vectorization...")
        
        if self.combined_data is None or len(self.combined_data) == 0:
            raise ValueError("No data available for vectorization")
        
        # Strategy 1: Standard TF-IDF for exact matching
        standard_texts = []
        # Strategy 2: Enhanced TF-IDF for semantic matching
        semantic_texts = []
        
        for _, row in self.combined_data.iterrows():
            # Standard text (primary translation only)
            standard_text = str(row.get('text', '')).strip()
            standard_texts.append(standard_text)
            
            # Enhanced semantic text (includes concepts, keywords, multiple translations)
            semantic_parts = [standard_text]
            
            # Add concept and keyword for semantic richness
            if str(row.get('Concept', '')).strip():
                semantic_parts.append(str(row['Concept']))
            if str(row.get('Keyword', '')).strip():
                semantic_parts.append(str(row['Keyword']))
            
            # Add additional context for Gita verses
            if row.get('source') == 'Gita':
                for col in ['Swami Gambirananda', 'Swami Sivananda']:
                    if col in row and str(row.get(col, '')).strip():
                        alt_translation = str(row[col]).strip()
                        if alt_translation != standard_text:
                            semantic_parts.append(alt_translation)
            
            semantic_texts.append(' '.join(semantic_parts))
        
        # Standard TF-IDF for precise matching
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=8000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
            norm='l2'
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(standard_texts)
        
        # Enhanced semantic TF-IDF for broader matching
        self.semantic_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=12000,
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.85,
            sublinear_tf=True,
            norm='l2'
        )
        self.semantic_matrix = self.semantic_vectorizer.fit_transform(semantic_texts)
        
        print(f"✓ Standard TF-IDF matrix: {self.tfidf_matrix.shape}")
        print(f"✓ Semantic TF-IDF matrix: {self.semantic_matrix.shape}")
    
    async def _load_modern_models(self):
        """Load modern AI models for summarization and translation"""
        print("🤖 Loading modern AI models...")
        
        try:
            # Load FLAN-T5 for better summarization (latest open-source model)
            model_name = "google/flan-t5-base"
            print(f"  📥 Loading {model_name} for summarization...")
            
            self.summary_tokenizer = T5Tokenizer.from_pretrained(model_name)
            self.summary_model = T5ForConditionalGeneration.from_pretrained(model_name)
            
            if torch.cuda.is_available():
                self.summary_model = self.summary_model.cuda()
                print("  🚀 Summary model loaded on GPU")
            else:
                print("  💻 Summary model loaded on CPU")
            
            # Load mT5 for translation (multilingual T5)
            translation_model = "google/mt5-base"
            print(f"  📥 Loading {translation_model} for translation...")
            
            self.translation_tokenizer = T5Tokenizer.from_pretrained(translation_model)
            self.translation_model = T5ForConditionalGeneration.from_pretrained(translation_model)
            
            if torch.cuda.is_available():
                self.translation_model = self.translation_model.cuda()
            
            print("✅ Modern AI models loaded successfully!")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load modern models: {e}")
            print("  📝 Falling back to text-based summaries")
    
    async def query(self, query: str, top_n: int = 5, source_filter: Optional[List[str]] = None) -> QueryResponse:
        """Enhanced query processing with hybrid retrieval"""
        start_time = time.time()
        
        if not self.combined_data is not None:
            raise ValueError("RAG service not initialized")
        
        print(f"🔍 Processing query: '{query}' (top_n={top_n})")
        
        # Enhanced query preprocessing
        processed_query = self._preprocess_query(query)
        
        # Hybrid retrieval: combine standard and semantic results
        verses, similarities = await self._hybrid_retrieve_verses(
            processed_query, top_n, source_filter
        )
        
        # Generate enhanced summary
        summary = await self._generate_enhanced_summary(query, verses)
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        return QueryResponse(
            query=query,
            retrieved_verses=verses,
            summary=summary,
            total_results=len(verses),
            processing_time_ms=processing_time
        )
    
    def _preprocess_query(self, query: str) -> str:
        """Enhanced query preprocessing"""
        # Convert to lowercase and clean
        processed = query.lower().strip()
        
        # Expand common spiritual terms
        expansions = {
            'mind': 'mind mental consciousness thought',
            'meditation': 'meditation dhyana mindfulness concentration',
            'dharma': 'dharma duty righteousness moral',
            'karma': 'karma action work deed',
            'moksha': 'moksha liberation freedom enlightenment',
            'yoga': 'yoga union practice discipline'
        }
        
        for term, expansion in expansions.items():
            if term in processed:
                processed = processed.replace(term, expansion)
        
        return processed
    
    async def _hybrid_retrieve_verses(self, query: str, top_n: int, source_filter: Optional[List[str]] = None) -> Tuple[List[Verse], np.ndarray]:
        """Hybrid retrieval combining standard and semantic approaches"""
        
        # Standard retrieval
        standard_query_vector = self.vectorizer.transform([query])
        standard_similarities = (self.tfidf_matrix @ standard_query_vector.T).toarray().ravel()
        
        # Semantic retrieval
        semantic_query_vector = self.semantic_vectorizer.transform([query])
        semantic_similarities = (self.semantic_matrix @ semantic_query_vector.T).toarray().ravel()
        
        # Combine similarities with weighted approach
        combined_similarities = (0.6 * standard_similarities + 0.4 * semantic_similarities)
        
        # Get top results
        top_indices = combined_similarities.argsort()[::-1]
        
        verses = []
        final_similarities = []
        
        for idx in top_indices:
            if len(verses) >= top_n:
                break
                
            row = self.combined_data.iloc[idx]
            source = row.get('source', 'Unknown')
            
            # Apply source filter
            if source_filter and source not in source_filter:
                continue
            
            # Skip very low similarity scores
            if combined_similarities[idx] < 0.01:
                continue
            
            # Create enhanced verse object
            verse = self._create_enhanced_verse(row, combined_similarities[idx])
            verses.append(verse)
            final_similarities.append(combined_similarities[idx])
        
        return verses, np.array(final_similarities)
    
    def _create_enhanced_verse(self, row: pd.Series, similarity_score: float) -> Verse:
        """Create enhanced verse object with complete information"""
        
        # Get Sanskrit text
        sanskrit_text = ""
        if 'sanskrit' in row and pd.notna(row['sanskrit']):
            sanskrit_text = str(row['sanskrit']).strip()
        
        # Get best English translation
        translation = self._get_best_translation(row)
        
        # Get chapter and verse numbers
        chapter = None
        verse_num = None
        
        if 'chapter' in row and pd.notna(row['chapter']):
            try:
                chapter = int(float(row['chapter']))
            except (ValueError, TypeError):
                pass
        
        if 'verse' in row and pd.notna(row['verse']):
            try:
                verse_num = int(float(row['verse']))
            except (ValueError, TypeError):
                pass
        
        # Get concept and keyword
        concept = str(row.get('Concept', '') or row.get('concept', '') or '').strip()
        keyword = str(row.get('Keyword', '') or row.get('keyword', '') or '').strip()
        
        return Verse(
            chapter=chapter,
            verse=verse_num,
            text=translation,
            sanskrit=sanskrit_text,
            translation=translation,
            source=SourceType(row.get('source', 'Unknown')),
            similarity_score=round(float(similarity_score), 4),
            concept=concept,
            keyword=keyword
        )
    
    def _get_best_translation(self, row: pd.Series) -> str:
        """Get the best available translation"""
        if row.get('source') == 'Gita':
            return self._get_best_gita_translation(row)
        else:
            # For PYS
            if 'translation' in row and pd.notna(row['translation']):
                return str(row['translation']).strip()
            if 'text' in row and pd.notna(row['text']):
                return str(row['text']).strip()
        return ""
    
    async def _generate_enhanced_summary(self, query: str, verses: List[Verse]) -> str:
        """Generate enhanced AI-powered summary"""
        if not verses:
            return "No relevant verses found for your query."
        
        # Create verse-by-verse analysis
        verse_summaries = []
        
        for i, verse in enumerate(verses, 1):
            summary_parts = []
            
            # Verse reference
            if verse.chapter and verse.verse:
                source_name = "Bhagavad Gita" if verse.source == SourceType.Gita else "Patanjali Yoga Sutras"
                reference = f"{source_name} {verse.chapter}.{verse.verse}"
                summary_parts.append(f"**{reference}**")
            else:
                summary_parts.append(f"**Verse {i}**")
            
            # Core teaching (first 120 chars for conciseness)
            if verse.translation:
                teaching = verse.translation.strip()
                if len(teaching) > 120:
                    teaching = teaching[:120] + "..."
                summary_parts.append(f": {teaching}")
            
            verse_summaries.append("".join(summary_parts))
        
        # Try AI-powered summary if models are available
        if self.summary_model and self.summary_tokenizer:
            try:
                ai_summary = await self._generate_ai_summary(query, verses)
                if ai_summary:
                    return f"**🔍 Query Analysis:** {ai_summary}\n\n**📖 Retrieved Verses:**\n" + "\n".join(verse_summaries)
            except Exception as e:
                print(f"AI summary generation failed: {e}")
        
        # Fallback to structured summary
        theme_analysis = self._analyze_themes(verses)
        
        summary_parts = [
            f"**🔍 Spiritual Guidance on '{query}'**\n",
            f"**📊 Analysis:** Found {len(verses)} relevant teachings " +
            f"from ancient scriptures with {theme_analysis}\n",
            "**📖 Key Verses:**\n" + "\n".join(verse_summaries),
            f"\n**💡 Teaching Summary:** These verses collectively guide us toward understanding " +
            f"'{query.lower()}' through the wisdom of dharma, self-discipline, and spiritual awareness."
        ]
        
        return "".join(summary_parts)
    
    async def _generate_ai_summary(self, query: str, verses: List[Verse]) -> str:
        """Generate AI-powered summary using FLAN-T5"""
        try:
            # Prepare input for AI model
            verse_texts = [v.translation[:100] for v in verses if v.translation][:3]  # Top 3 for context
            combined_text = " ".join(verse_texts)
            
            prompt = f"Summarize the spiritual teachings about '{query}' from these ancient verses: {combined_text}"
            
            # Tokenize and generate
            inputs = self.summary_tokenizer(
                prompt, 
                return_tensors="pt", 
                max_length=400,
                truncation=True
            )
            
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate with better parameters
            with torch.no_grad():
                outputs = self.summary_model.generate(
                    **inputs,
                    max_length=150,
                    min_length=40,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    temperature=0.7
                )
            
            summary = self.summary_tokenizer.decode(outputs[0], skip_special_tokens=True)
            return summary.strip() if summary else ""
            
        except Exception as e:
            print(f"AI summary generation error: {e}")
            return ""
    
    def _analyze_themes(self, verses: List[Verse]) -> str:
        """Analyze common themes in retrieved verses"""
        concepts = [v.concept for v in verses if v.concept]
        keywords = [v.keyword for v in verses if v.keyword]
        
        if concepts:
            return f"themes of {', '.join(set(concepts[:3]))}"
        elif keywords:
            return f"concepts of {', '.join(set(keywords[:3]))}"
        else:
            return "universal spiritual principles"
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language using mT5"""
        if target_language not in self.supported_languages:
            return f"Language '{target_language}' not supported. Available: {list(self.supported_languages.keys())}"
        
        if not self.translation_model or not self.translation_tokenizer:
            return "Translation model not available"
        
        try:
            # Prepare translation prompt
            lang_name = self.supported_languages[target_language]
            prompt = f"translate English to {lang_name}: {text}"
            
            inputs = self.translation_tokenizer(
                prompt,
                return_tensors="pt",
                max_length=256,
                truncation=True
            )
            
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.translation_model.generate(
                    **inputs,
                    max_length=200,
                    num_beams=3,
                    early_stopping=True
                )
            
            translation = self.translation_tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translation.strip()
            
        except Exception as e:
            return f"Translation failed: {e}"
    
    def get_sources(self) -> SourcesResponse:
        """Get information about available sources"""
        sources = []
        total_verses = 0
        
        for code, info in self.sources_info.items():
            sources.append(SourceInfo(
                name=info['name'],
                code=code,
                total_verses=info['total_verses'],
                chapters=info['chapters'],
                description=info['description']
            ))
            total_verses += info['total_verses']
        
        return SourcesResponse(
            sources=sources,
            total_verses=total_verses
        )
    
    def _is_query_valid(self, query: str) -> bool:
        """Enhanced query validation"""
        if not query or len(query.strip()) < 2:
            return False
        
        # Check for inappropriate content
        inappropriate_keywords = {
            'abuse', 'hate', 'violence', 'illegal', 'harmful',
            'offensive', 'inappropriate', 'vulgar'
        }
        
        query_lower = query.lower()
        return not any(keyword in query_lower for keyword in inappropriate_keywords)

