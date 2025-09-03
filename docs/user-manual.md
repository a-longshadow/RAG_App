# User Manual - RAG Document System

## 🎯 **GETTING STARTED**

Welcome to your AI-powered document question-answering system! This guide will help you upload documents, ask questions, and get intelligent responses powered by 100+ AI models.

### **Quick Start (2 minutes)**
1. **Open**: http://127.0.0.1:8000/ in your browser
2. **Upload**: Drag & drop a document (PDF, Word, Markdown, etc.)
3. **Wait**: System processes your document (usually 10-30 seconds)
4. **Ask**: Type a question about your document
5. **Get Answer**: Receive AI-powered response with sources

### **What You Can Do**
- 📄 **Upload any document**: PDFs, Word docs, Markdown files, JSON data
- 🤖 **Choose AI model**: Claude, GPT-4, Gemini, Llama, and 100+ others
- 🎯 **Target specific documents**: Select which documents to search
- 📊 **Track performance**: View analytics and conversation history
- 🔧 **Test models**: Try different AI models before using them

## 📋 **MAIN INTERFACE**

### **Home Page** (`/`)
Your main workspace for uploading documents and choosing your query interface.

#### **Upload Area**
- **Drag & Drop**: Simply drag files from your computer
- **Click to Browse**: Use the file picker
- **Multiple Files**: Upload several documents at once
- **Supported Formats**: PDF, DOCX, MD, TXT, JSON, CSV
- **File Size Limit**: 5MB per file

#### **Query Interface Selection**
Choose between two powerful interfaces:

**💬 Chat Interface** (Recommended)
- **Best For**: General users, quick questions, document exploration
- **Features**: ChatGPT-style conversation, real-time responses, natural language
- **Use When**: Asking questions, exploring documents, getting quick answers
- **Access**: Green "Chat" button or navigate to `/chat/`

**🔍 Advanced Query** (Developer)
- **Best For**: Developers, researchers, detailed analysis
- **Features**: Similarity thresholds, performance metrics, detailed source attribution
- **Use When**: Research, debugging search performance, API development
- **Access**: Blue "Advanced Query" button or navigate to `/query/`

## 💬 **CHAT INTERFACE** (`/chat/`)

### **ChatGPT-Style Experience**
Modern conversational interface for natural document interaction.

#### **How to Use**
1. **Type Message**: Enter your question naturally
2. **Send**: Press Enter or click Send button
3. **View Response**: See AI response with visual indicators
4. **Continue**: Ask follow-up questions in same conversation

#### **Response Types**
**🔵 LLM-Only Responses** (Blue badge)
- Pure conversational responses for greetings, capabilities
- No document search performed
- Instant responses for general questions

**🟢 Document-Based Responses** (Green badge)  
- RAG-enhanced responses using your documents
- Shows chunk count and search metrics
- Includes source document references

#### **Features**
- **Real-Time Chat**: Instant message exchange
- **Typing Indicators**: See when AI is thinking
- **Copy Responses**: Click to copy AI answers
- **Message History**: Scroll through conversation
- **Performance Info**: See response times and model used

## 🔍 **ADVANCED QUERY INTERFACE** (`/query/`)

### **Developer-Focused Experience**
Detailed query interface with comprehensive metrics and controls.

#### **Query Form**
- **Question Box**: Type your question
- **Model Selector**: Choose specific AI model
- **Document Selector**: Pick which documents to search
- **Similarity Threshold**: Adjust search sensitivity (0.1-0.9)
- **Max Results**: Control number of source chunks (1-20)

#### **Response Display**
- **AI Answer**: Comprehensive response with formatting
- **Performance Metrics**: Detailed timing breakdown
  - Search Time: How long to find relevant chunks
  - LLM Time: How long for AI to generate response
  - Total Time: Complete processing time
- **Source Chunks**: Detailed source information
  - Document name and file
  - Similarity score for each chunk
  - Exact text sections referenced
  - Character positions in source document

#### **Advanced Features**
- **Document Filtering**: Search only selected documents
- **Threshold Tuning**: Adjust relevance requirements
- **Debug Information**: Detailed search diagnostics
- **API-Ready**: JSON responses available for integration

## 📚 **DOCUMENT MANAGEMENT**

### **Document Library** (`/documents/`)
View and manage all your uploaded documents.

#### **Document Cards**
Each document shows:
- **Title**: Document name
- **Type**: File format (PDF, DOCX, etc.)
- **Size**: File size
- **Chunks**: How many searchable sections
- **Upload Date**: When you added it
- **Actions**: Delete or view details

#### **Document Processing**
When you upload a document:
1. **Text Extraction**: System reads the content
2. **Chunking**: Breaks into searchable sections
3. **Embedding**: Creates AI-searchable vectors
4. **Indexing**: Adds to search database
5. **Ready**: Available for questions

#### **Supported File Types**
- **PDF**: Any PDF document
- **Word**: .docx files
- **Markdown**: .md files
- **Text**: .txt files
- **JSON**: Structured data
- **CSV**: Spreadsheet data

## 🤖 **AI MODEL SELECTION**

### **Model Selector** (`/models/`)
Choose from 100+ AI models for different needs.

#### **Featured Models**
- **Claude 3.5 Sonnet**: Best overall, great reasoning
- **GPT-4o**: Excellent for complex questions
- **Gemini 2.5 Flash**: Fast and accurate
- **Claude 3 Haiku**: Budget-friendly option
- **DeepSeek R1**: Great for technical questions

#### **Model Categories**
- **Chat Models**: Best for conversations
- **Reasoning**: For complex analysis
- **Fast**: Quick responses
- **Budget**: Cost-effective options
- **Specialized**: Coding, math, creative writing

#### **Model Information**
Each model shows:
- **Name & Provider**: Who made it
- **Context Length**: How much text it can process
- **Pricing**: Cost per 1000 tokens
- **Description**: What it's good for
- **Test Button**: Try it before using

#### **Testing Models**
1. **Select Model**: Click on any model
2. **Test Message**: Type a sample question
3. **Get Response**: See how it answers
4. **Check Performance**: Response time and quality
5. **Select for Use**: If satisfied, use for your documents

## 🔍 **ASKING QUESTIONS**

### **How to Ask Good Questions**
- **Be Specific**: "What are the key features?" vs "Tell me about features"
- **Use Context**: "In the API documentation, what is the rate limit?"
- **Ask Follow-ups**: Build on previous responses
- **Reference Sections**: "According to chapter 3..."

### **Question Types That Work Well**
- **Factual**: "What is the pricing model?"
- **Analytical**: "What are the pros and cons of this approach?"
- **Procedural**: "How do I set up authentication?"
- **Comparative**: "What's the difference between Plan A and Plan B?"
- **Summarization**: "Summarize the key findings"

### **Document Selection**
- **All Documents**: Search everything (default)
- **Specific Documents**: Select 1-3 relevant documents
- **Similar Topics**: Group related documents
- **Performance**: Fewer documents = faster responses

### **Model Selection Tips**
- **Quick Questions**: Use Claude 3 Haiku or Gemini Flash
- **Complex Analysis**: Use Claude 3.5 Sonnet or GPT-4o
- **Technical Docs**: Use DeepSeek or specialized coding models
- **Creative Tasks**: Use Claude or GPT models
- **Budget Conscious**: Use smaller/faster models

## 📊 **ANALYTICS & TRACKING**

### **Analytics Dashboard** (`/analytics/`)
Monitor system performance and usage patterns.

#### **Overview Stats**
- **Total Queries**: How many questions asked
- **Documents Uploaded**: Number of files processed
- **Average Response Time**: How fast the system responds
- **Most Used Model**: Your preferred AI model

#### **Performance Metrics**
- **Query Success Rate**: Percentage of successful responses
- **Average Similarity Score**: How relevant responses are
- **Response Time Trends**: Performance over time
- **Model Performance**: Which models work best

#### **Usage Patterns**
- **Popular Documents**: Most queried files
- **Question Categories**: Types of questions asked
- **Peak Usage Times**: When you use the system most
- **Model Preferences**: Which AI models you prefer

### **Conversation History** (`/conversations/`)
Review all your previous questions and responses.

#### **Session Tracking**
- **Session Groups**: Related questions grouped together
- **Conversation Flow**: See question progression
- **Context Building**: How questions build on each other
- **Session Analytics**: Performance per conversation

#### **Search & Filter**
- **Search Queries**: Find specific questions
- **Filter by Model**: See responses from specific AI models
- **Filter by Document**: Questions about specific files
- **Date Ranges**: Questions from specific time periods

## 🔧 **TROUBLESHOOTING**

### **Common Issues & Solutions**

#### **No AI Response**
- **Check Internet**: AI models need internet connection
- **Verify API Key**: OpenRouter key must be valid
- **Try Different Model**: Some models may be unavailable
- **Check Document Selection**: Make sure documents are selected

#### **Slow Responses**
- **Select Fewer Documents**: Limit to 1-3 most relevant
- **Use Faster Models**: Try Gemini Flash or Claude Haiku
- **Check File Size**: Large documents take longer to process
- **Clear Browser Cache**: Sometimes helps with performance

#### **Poor Answer Quality**
- **Be More Specific**: Add context to your questions
- **Select Relevant Documents**: Choose documents likely to contain answers
- **Try Better Models**: Claude 3.5 Sonnet or GPT-4o for complex questions
- **Rephrase Question**: Sometimes different wording helps

#### **Upload Failures**
- **Check File Size**: Must be under 5MB
- **Supported Formats**: Use PDF, DOCX, MD, TXT, JSON, CSV
- **File Corruption**: Try re-saving the file
- **Browser Issues**: Try refreshing or different browser

#### **No Search Results**
- **Check Similarity Threshold**: Default is 0.1 - if no results, lower to 0.05
- **Verify Document Processing**: Make sure documents show "Processed" status
- **Try Broader Questions**: Be less specific initially
- **Check Document Content**: Ensure documents contain relevant text
- **Embedding Status**: Wait for documents to finish processing completely

#### **Interface Confusion**
- **Chat vs Advanced**: Use Chat for conversations, Advanced for detailed analysis
- **Green Badges**: Document-based responses using your files
- **Blue Badges**: LLM-only responses for general questions
- **Performance Metrics**: Visible in both interfaces with timing breakdown

#### **Rate Limiting Errors**
- **Free Models**: System defaults to google/gemini-2.5-flash (free)
- **Model Selection**: Switch to other free models if hitting limits
- **Fallback System**: Chat interface automatically falls back to templates
- **Wait Period**: Rate limits usually reset within 1-2 minutes

#### **SearchResult Errors** (For Developers)
- **Attribute Access**: Use `chunk.chunk.document` not `chunk.document`
- **Template Updates**: Clear browser cache after template changes
- **Debug Mode**: Enable Django debug for detailed error traces
- **Test Scripts**: Use `test_rag_system.py` for quick diagnostics

### **Performance Tips**

#### **For Best Results**
- **Quality Documents**: Upload well-formatted, clear documents
- **Relevant Questions**: Ask about content likely to be in your documents
- **Appropriate Models**: Match model to question complexity
- **Document Organization**: Group related documents together

#### **For Speed**
- **Select Specific Documents**: Don't search all documents for specific questions
- **Use Fast Models**: Gemini Flash, Claude Haiku for quick answers
- **Smaller Documents**: Break large files into sections
- **Clear Sessions**: Start fresh conversations for new topics

## 🎯 **BEST PRACTICES**

### **Document Preparation**
1. **Clean Formatting**: Remove extra spaces, fix headers
2. **Clear Structure**: Use headings and sections
3. **Relevant Content**: Only upload documents you'll query
4. **Reasonable Size**: Keep files under 2MB for best performance
5. **Descriptive Names**: Use clear, searchable titles

### **Effective Querying**
1. **Start Broad**: Begin with general questions
2. **Get Specific**: Follow up with detailed questions
3. **Use Context**: Reference previous responses
4. **Try Different Models**: Experiment to find what works best
5. **Build Conversations**: Let questions flow naturally

### **Model Selection Strategy**
1. **Match Complexity**: Simple questions → fast models, complex → powerful models
2. **Consider Cost**: Balance quality vs. expense
3. **Test First**: Use model testing feature
4. **Track Performance**: Monitor which models work best for you
5. **Stay Updated**: New models are added regularly

### **System Maintenance**
1. **Regular Cleanup**: Remove outdated documents
2. **Monitor Performance**: Check analytics regularly
3. **Update Documents**: Replace old versions with new ones
4. **Review Conversations**: Learn from past interactions
5. **Optimize Selection**: Refine document and model choices

## 🚀 **ADVANCED FEATURES**

### **Session Management**
- **Conversation Context**: System remembers your conversation flow
- **Session Grouping**: Related questions are grouped together
- **Context Building**: Each question can build on previous responses
- **Session Analytics**: Track performance within conversations

### **Model Testing**
- **Before Use**: Test any model with sample questions
- **Performance Comparison**: Compare response quality across models
- **Cost Estimation**: See pricing before committing
- **Response Time**: Check speed for your use case

### **Analytics Integration**
- **Performance Tracking**: Monitor system effectiveness
- **Usage Patterns**: Understand your workflow
- **Optimization Insights**: Improve based on data
- **Historical Analysis**: Track improvements over time

### **Bulk Operations**
- **Multiple Document Upload**: Process several files at once
- **Batch Processing**: System handles multiple documents efficiently
- **Mass Selection**: Select multiple documents for queries
- **Bulk Management**: Organize documents in groups

## 📞 **SUPPORT & RESOURCES**

### **Getting Help**
- **Documentation**: Check this user manual first
- **Error Messages**: Read system notifications for guidance
- **Analytics**: Review performance data for insights
- **Model Testing**: Use test feature to troubleshoot

### **System Status**
- **Health Check**: Visit `/models/` to verify system is working
- **Model Availability**: Check if AI models are accessible
- **Document Processing**: Verify uploads are working
- **Response Quality**: Test with known questions

### **Tips for Success**
1. **Start Simple**: Begin with basic questions
2. **Experiment**: Try different models and approaches
3. **Organize**: Keep documents well-organized
4. **Monitor**: Use analytics to improve performance
5. **Iterate**: Refine your approach based on results

**Ready to get intelligent answers from your documents!** 🎉
