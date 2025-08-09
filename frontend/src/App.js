import React, { useState, useEffect } from 'react';
import { Search, BookOpen, Heart, Sparkles, Clock, Target, ChevronDown, ChevronUp } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sourcesInfo, setSourcesInfo] = useState(null);
  const [expandedVerse, setExpandedVerse] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);

  // Sample queries for quick access
  const sampleQueries = [
    "How to control the mind?",
    "What is the purpose of life?",
    "How to overcome fear?",
    "What is true happiness?",
    "How to find inner peace?",
    "What is meditation?",
    "How to deal with suffering?",
    "What is dharma?"
  ];

  useEffect(() => {
    fetchSourcesInfo();
    loadSearchHistory();
  }, []);

  const fetchSourcesInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/sources`);
      setSourcesInfo(response.data);
    } catch (err) {
      console.error('Error fetching sources info:', err);
    }
  };

  const loadSearchHistory = () => {
    const history = localStorage.getItem('searchHistory');
    if (history) {
      setSearchHistory(JSON.parse(history));
    }
  };

  const saveToHistory = (query) => {
    const newHistory = [query, ...searchHistory.filter(q => q !== query)].slice(0, 5);
    setSearchHistory(newHistory);
    localStorage.setItem('searchHistory', JSON.stringify(newHistory));
  };

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        query: searchQuery,
        top_n: 5,
        include_summary: true
      });

      setResults(response.data);
      saveToHistory(searchQuery);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while processing your query');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const toggleVerse = (index) => {
    setExpandedVerse(expandedVerse === index ? null : index);
  };

  return (
    <div className="min-h-screen spiritual-gradient">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-4xl">🕉️</div>
              <div>
                <h1 className="text-2xl font-bold text-white elegant-heading">
                  Spiritual Wisdom Explorer
                </h1>
                <p className="text-white/80">Discover timeless teachings from sacred texts</p>
              </div>
            </div>
            
            {sourcesInfo && (
              <div className="hidden md:flex items-center space-x-6 text-white/90">
                <div className="text-center">
                  <div className="text-2xl font-bold">{sourcesInfo.total_verses}</div>
                  <div className="text-sm">Total Verses</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{sourcesInfo.sources.length}</div>
                  <div className="text-sm">Sacred Texts</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Search Section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 elegant-heading">
            Ask the Ancient Wisdom
          </h2>
          <p className="text-white/90 text-lg mb-8 max-w-2xl mx-auto">
            Explore profound teachings from the Bhagavad Gita and Patanjali Yoga Sutras. 
            Ask any spiritual question and discover relevant verses with modern AI insights.
          </p>

          {/* Search Input */}
          <div className="max-w-2xl mx-auto mb-6">
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a spiritual question... (e.g., How to find inner peace?)"
                className="search-input pr-12"
                disabled={loading}
              />
              <button
                onClick={() => handleSearch()}
                disabled={loading || !query.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-spiritual-500 hover:text-spiritual-700 disabled:opacity-50"
              >
                <Search size={24} />
              </button>
            </div>
          </div>

          {/* Sample Queries */}
          <div className="max-w-4xl mx-auto mb-8">
            <p className="text-white/80 mb-3">Try these popular questions:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {sampleQueries.map((sampleQuery, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(sampleQuery);
                    handleSearch(sampleQuery);
                  }}
                  className="btn-secondary text-sm"
                  disabled={loading}
                >
                  {sampleQuery}
                </button>
              ))}
            </div>
          </div>

          {/* Search History */}
          {searchHistory.length > 0 && (
            <div className="max-w-2xl mx-auto">
              <p className="text-white/80 mb-2">Recent searches:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {searchHistory.map((historyQuery, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setQuery(historyQuery);
                      handleSearch(historyQuery);
                    }}
                    className="btn-secondary text-sm opacity-75 hover:opacity-100"
                    disabled={loading}
                  >
                    <Clock size={14} className="mr-1" />
                    {historyQuery}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-flex items-center space-x-3 bg-white/90 backdrop-blur-sm rounded-xl px-6 py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-spiritual-500"></div>
              <span className="text-spiritual-700 font-medium">Searching sacred wisdom...</span>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-8">
            <div className="bg-red-100/90 backdrop-blur-sm border border-red-200 text-red-700 px-6 py-4 rounded-xl max-w-2xl mx-auto">
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-8 animate-fade-in">
            {/* Query Summary */}
            <div className="text-center">
              <h3 className="text-2xl font-bold text-white mb-2 elegant-heading">
                Results for: "{results.query}"
              </h3>
              <div className="flex justify-center items-center space-x-6 text-white/80">
                <span className="flex items-center">
                  <Target size={16} className="mr-1" />
                  {results.total_results} verses found
                </span>
                <span className="flex items-center">
                  <Clock size={16} className="mr-1" />
                  {results.processing_time_ms}ms
                </span>
              </div>
            </div>

            {/* AI Summary */}
            {results.summary && (
              <div className="verse-card max-w-4xl mx-auto">
                <div className="flex items-start space-x-3 mb-4">
                  <Sparkles className="text-spiritual-500 mt-1" size={24} />
                  <div>
                    <h4 className="text-xl font-semibold text-spiritual-800 mb-2 elegant-heading">
                      AI-Generated Insight
                    </h4>
                    <div className="prose prose-spiritual max-w-none">
                      <ReactMarkdown>{results.summary}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Verses */}
            <div className="space-y-6">
              <h4 className="text-xl font-semibold text-white text-center elegant-heading">
                Relevant Sacred Verses
              </h4>
              
              {results.retrieved_verses.map((verse, index) => (
                <div key={index} className="verse-card animate-slide-up" style={{animationDelay: `${index * 100}ms`}}>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center space-x-3">
                      <BookOpen className="text-spiritual-500" size={20} />
                      <div>
                        <span className="font-semibold text-spiritual-800">
                          {verse.source === 'Gita' ? 'Bhagavad Gita' : 'Patanjali Yoga Sutras'}
                        </span>
                        {verse.chapter && verse.verse && (
                          <span className="text-spiritual-600 ml-2">
                            {verse.chapter}.{verse.verse}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="bg-spiritual-100 text-spiritual-700 px-2 py-1 rounded text-sm">
                        {Math.round(verse.similarity_score * 100)}% Relevance Match
                      </div>
                      <button
                        onClick={() => toggleVerse(index)}
                        className="text-spiritual-500 hover:text-spiritual-700"
                      >
                        {expandedVerse === index ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                      </button>
                    </div>
                  </div>

                  {/* Sanskrit and Translation */}
                  <div className="mb-4 space-y-3">
                    {/* Sanskrit Text */}
                    {verse.sanskrit && (
                      <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg">
                        <div className="text-sm font-semibold text-amber-800 mb-2">Sanskrit</div>
                        <p className="text-amber-900 text-lg font-medium" style={{fontFamily: 'serif'}}>
                          {verse.sanskrit}
                        </p>
                      </div>
                    )}
                    
                    {/* English Translation */}
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
                      <div className="text-sm font-semibold text-blue-800 mb-2">English Translation</div>
                      <p className="text-blue-900 text-lg leading-relaxed italic">
                        "{verse.translation || verse.text}"
                      </p>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {expandedVerse === index && (
                    <div className="border-t border-spiritual-200 pt-4 space-y-3">
                      {/* Chapter and Verse Number */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {verse.chapter && (
                          <div>
                            <span className="font-medium text-spiritual-700">Chapter: </span>
                            <span className="text-gray-700">{verse.chapter}</span>
                          </div>
                        )}
                        {verse.verse && (
                          <div>
                            <span className="font-medium text-spiritual-700">Verse: </span>
                            <span className="text-gray-700">{verse.verse}</span>
                          </div>
                        )}
                      </div>
                      
                      {/* Reference */}
                      {verse.chapter && verse.verse && (
                        <div className="bg-spiritual-50 rounded-lg p-3">
                          <span className="font-medium text-spiritual-700">Reference: </span>
                          <span className="text-spiritual-800 font-semibold">
                            {verse.source === 'Gita' ? 'Bhagavad Gita' : 'Patanjali Yoga Sutras'} {verse.chapter}.{verse.verse}
                          </span>
                        </div>
                      )}
                      
                      {verse.concept && (
                        <div>
                          <span className="font-medium text-spiritual-700">Concept: </span>
                          <span className="text-gray-700">{verse.concept}</span>
                        </div>
                      )}
                      {verse.keyword && (
                        <div>
                          <span className="font-medium text-spiritual-700">Key Term: </span>
                          <span className="text-gray-700">{verse.keyword}</span>
                        </div>
                      )}
                      <div>
                        <span className="font-medium text-spiritual-700">Relevance Score: </span>
                        <span className="text-gray-700">{(verse.similarity_score * 100).toFixed(1)}% relevance match</span>
                      </div>

                    </div>
                  )}

                  {/* Concept Tag */}
                  {verse.concept && (
                    <div className="flex items-center mt-4">
                      <Heart className="text-red-400 mr-2" size={16} />
                      <span className="bg-gradient-to-r from-spiritual-100 to-saffron-100 text-spiritual-800 px-3 py-1 rounded-full text-sm font-medium">
                        {verse.concept}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="text-center text-white/70 mt-16 pb-8">
          <div className="border-t border-white/20 pt-8">
            <p className="mb-2">
              Built with ❤️ to make ancient wisdom accessible through modern technology
            </p>
            <p className="text-sm">
              Powered by AI • Sourced from Sacred Texts • Made for Spiritual Seekers
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;

