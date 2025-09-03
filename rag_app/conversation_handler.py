"""
Conversation handler for casual and system queries
"""
import re
import random
from typing import Optional, Dict, Any
from django.contrib.auth.models import User


class ConversationHandler:
    """
    Handles conversational queries that don't require document search
    """
    
    def __init__(self):
        self.greeting_responses = [
            "Hello! 👋 I'm your AI document assistant. I can help you find information in your uploaded documents or answer questions about the system. What would you like to know?",
            "Hi there! Welcome to your document search system. Upload some documents and I'll help you find answers within them. How can I assist you today?",
            "Hey! I'm here to help you search through your documents intelligently. Feel free to ask me anything about your uploaded files or how the system works.",
            "Hello! Ready to explore your documents together? I can search through your files and provide AI-powered answers. What's your question?"
        ]
        
        self.hear_me_responses = [
            "Yes, I can hear you! 🎯 I'm here and ready to help. You can ask me questions about any documents you've uploaded, or I can help you understand how the system works. What would you like to know?",
            "Loud and clear! I'm your AI assistant for document search and analysis. Upload some documents and start asking questions - I'll find the relevant information for you.",
            "I hear you perfectly! Ready to help you search through documents and find answers. Have you uploaded any documents yet? If so, what would you like to know about them?",
            "Yes, I'm listening! 👂 I specialize in helping you find information within your document library. What can I help you discover today?"
        ]
        
        self.capability_responses = [
            """I can help you with several things:
            
📄 **Document Processing**: Upload PDFs, Word docs, Markdown, JSON, CSV files
🔍 **Smart Search**: Find relevant information using AI-powered semantic search  
🤖 **AI Models**: Choose from 100+ models (Claude, GPT-4, Gemini, Llama, etc.)
📊 **Analytics**: Track your queries and system performance
💬 **Conversations**: Have natural discussions about your document content

Try uploading a document and asking me questions about it!""",
            
            """Here's what I can do for you:
            
✨ **Upload & Process**: Handle multiple document formats automatically
🎯 **Target Search**: Select specific documents to search within
💡 **Intelligent Answers**: Use advanced AI models for comprehensive responses
📈 **Performance Tracking**: Monitor search accuracy and response times
🔧 **Model Testing**: Try different AI models to find what works best

What would you like to start with?""",
            
            """I'm designed to be your intelligent document assistant:
            
🚀 **Quick Setup**: Drag & drop documents, instant processing
🧠 **Smart Analysis**: Understand context and provide relevant answers
⚡ **Fast Search**: Find information in seconds across all your files
🎨 **Multiple Models**: Access latest AI technology (Claude 3.5, GPT-4o, Gemini 2.5)
📊 **Usage Analytics**: See how your queries perform over time

Ready to get started?"""
        ]
        
        self.system_info = {
            'models': "I have access to 100+ AI models including Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Flash, Llama 3.1, DeepSeek R1, and many more. You can test and select different models based on your needs.",
            'formats': "I support PDF, Word documents (.docx), Markdown (.md), text files (.txt), JSON data, and CSV spreadsheets. Just drag and drop your files!",
            'upload': "To upload documents, simply drag and drop files onto the upload area on the home page, or click to browse your files. I'll process them automatically and make them searchable.",
            'search': "Ask me natural language questions about your documents. I'll find relevant sections and provide AI-generated answers with source citations.",
            'privacy': "Your documents are processed locally with embeddings stored securely. AI responses come through OpenRouter's API, but your document content stays private."
        }
        
        # Patterns for conversation classification
        self.greeting_patterns = [
            r'\b(hello|hi|hey|greetings|good\s+(morning|afternoon|evening))\b',
            r'\b(what\'s\s+up|how\s+are\s+you|how\s+do\s+you\s+do)\b'
        ]
        
        self.hear_patterns = [
            r'\b(can\s+you\s+hear\s+me|are\s+you\s+there|are\s+you\s+listening)\b',
            r'\b(hello\s+there|anybody\s+home|respond\s+if\s+you\s+can)\b'
        ]
        
        self.capability_patterns = [
            r'\b(what\s+can\s+you\s+do|what\s+are\s+your\s+capabilities|help\s+me)\b',
            r'\b(how\s+does\s+this\s+work|what\s+is\s+this|explain\s+the\s+system)\b',
            r'\b(what\s+are\s+you|who\s+are\s+you|tell\s+me\s+about\s+yourself)\b'
        ]
        
        self.model_patterns = [
            r'\b(what\s+models|which\s+ai|available\s+models|list\s+models)\b',
            r'\b(ai\s+options|model\s+selection|choose\s+model)\b'
        ]
        
        self.format_patterns = [
            r'\b(what\s+formats|file\s+types|supported\s+files|upload\s+types)\b',
            r'\b(can\s+i\s+upload|file\s+support|document\s+types)\b'
        ]
        
        self.upload_patterns = [
            r'\b(how\s+to\s+upload|upload\s+documents|add\s+files|how\s+do\s+i\s+upload)\b',
            r'\b(upload\s+process|add\s+document|insert\s+file)\b'
        ]
    
    def classify_query(self, query: str) -> str:
        """
        Classify the type of conversational query
        
        Returns: 'greeting', 'hear_me', 'capability', 'system', 'document', or None
        """
        query_lower = query.lower().strip()
        
        # Check for greeting patterns
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.greeting_patterns):
            return 'greeting'
        
        # Check for "can you hear me" patterns
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.hear_patterns):
            return 'hear_me'
        
        # Check for capability questions
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.capability_patterns):
            return 'capability'
        
        # Check for system-specific questions
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.model_patterns):
            return 'models'
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.format_patterns):
            return 'formats'
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.upload_patterns):
            return 'upload'
        
        # If no conversational pattern matches, it's likely a document query
        return 'document'
    
    def handle_conversational_query(self, query: str, user: Optional[User] = None) -> Optional[str]:
        """
        Generate response for conversational queries
        
        Args:
            query: User's query
            user: Authenticated user (optional)
            
        Returns:
            Conversational response or None if it's a document query
        """
        category = self.classify_query(query)
        
        if category == 'greeting':
            response = random.choice(self.greeting_responses)
            if user and user.is_authenticated:
                # Get user's document count for personalization
                from .models import Document
                doc_count = Document.objects.filter(uploaded_by=user).count()
                if doc_count > 0:
                    response += f"\n\nI see you have {doc_count} document{'s' if doc_count != 1 else ''} in your library. Feel free to ask me questions about them!"
            return response
        
        elif category == 'hear_me':
            response = random.choice(self.hear_me_responses)
            if user and user.is_authenticated:
                from .models import Document
                doc_count = Document.objects.filter(uploaded_by=user).count()
                if doc_count == 0:
                    response += "\n\n💡 **Tip**: Upload some documents first, then I can help you search through them!"
            return response
        
        elif category == 'capability':
            return random.choice(self.capability_responses)
        
        elif category in ['models', 'formats', 'upload']:
            return self.system_info.get(category, "I can help with that! Please be more specific about what you'd like to know.")
        
        # If it's a document query, return None so the RAG engine handles it
        return None
    
    def get_context_aware_response(self, query: str, user: Optional[User] = None, has_documents: bool = False) -> Optional[str]:
        """
        Generate context-aware conversational response
        
        Args:
            query: User's query
            user: Authenticated user
            has_documents: Whether user has uploaded documents
            
        Returns:
            Contextual response or None for document queries
        """
        response = self.handle_conversational_query(query, user)
        
        if response and not has_documents and user and user.is_authenticated:
            # Add helpful guidance for users with no documents
            response += "\n\n🚀 **Get Started**: Upload your first document using the drag & drop area above!"
        
        return response


# Global conversation handler instance
_conversation_handler = None

def get_conversation_handler() -> ConversationHandler:
    """Get global conversation handler instance"""
    global _conversation_handler
    if _conversation_handler is None:
        _conversation_handler = ConversationHandler()
    return _conversation_handler
