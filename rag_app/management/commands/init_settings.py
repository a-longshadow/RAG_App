"""
Management command to initialize system settings for RAG configuration
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rag_app.models import SystemSettings


class Command(BaseCommand):
    help = 'Initialize default system settings for RAG configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing settings to defaults',
        )
    
    def handle(self, *args, **options):
        """Initialize system settings"""
        reset = options['reset']
        
        # Default settings configuration
        default_settings = [
            {
                'key': 'rag_similarity_threshold',
                'value': '0.3',
                'value_type': 'float',
                'description': 'Minimum similarity score for chunk retrieval (0.0-1.0)'
            },
            {
                'key': 'rag_max_chunks',
                'value': '5',
                'value_type': 'integer',
                'description': 'Maximum number of chunks to retrieve for context'
            },
            {
                'key': 'rag_max_context_length',
                'value': '4000',
                'value_type': 'integer',
                'description': 'Maximum character length for assembled context'
            },
            {
                'key': 'rag_embedding_model',
                'value': 'all-mpnet-base-v2',
                'value_type': 'string',
                'description': 'Sentence transformer model for embeddings'
            },
            {
                'key': 'rag_llm_model',
                'value': 'anthropic/claude-3-sonnet',
                'value_type': 'string',
                'description': 'OpenRouter model for response generation'
            },
            {
                'key': 'rag_temperature',
                'value': '0.7',
                'value_type': 'float',
                'description': 'LLM temperature for response generation (0.0-2.0)'
            },
            {
                'key': 'rag_max_tokens',
                'value': '1000',
                'value_type': 'integer',
                'description': 'Maximum tokens for LLM response'
            },
            {
                'key': 'rag_include_metadata',
                'value': 'true',
                'value_type': 'boolean',
                'description': 'Include document metadata in context'
            },
            
            # Document processing settings
            {
                'key': 'doc_chunk_size',
                'value': '500',
                'value_type': 'integer',
                'description': 'Default chunk size for document processing'
            },
            {
                'key': 'doc_chunk_overlap',
                'value': '50',
                'value_type': 'integer',
                'description': 'Character overlap between document chunks'
            },
            {
                'key': 'doc_max_file_size',
                'value': '5242880',
                'value_type': 'integer',
                'description': 'Maximum file size in bytes (5MB default)'
            },
            
            # System behavior settings
            {
                'key': 'sys_enable_background_processing',
                'value': 'true',
                'value_type': 'boolean',
                'description': 'Enable background processing for document uploads'
            },
            {
                'key': 'sys_log_queries',
                'value': 'true',
                'value_type': 'boolean',
                'description': 'Log user queries and responses'
            },
            {
                'key': 'sys_enable_analytics',
                'value': 'true',
                'value_type': 'boolean',
                'description': 'Enable usage analytics and performance tracking'
            },
        ]
        
        admin_user = None
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
        except:
            pass
        
        created_count = 0
        updated_count = 0
        
        for setting_data in default_settings:
            setting, created = SystemSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults={
                    'value': setting_data['value'],
                    'value_type': setting_data['value_type'],
                    'description': setting_data['description'],
                    'updated_by': admin_user,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created setting: {setting_data['key']}")
                )
            elif reset:
                # Update existing setting if reset flag is provided
                setting.value = setting_data['value']
                setting.value_type = setting_data['value_type']
                setting.description = setting_data['description']
                setting.updated_by = admin_user
                setting.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"🔄 Updated setting: {setting_data['key']}")
                )
            else:
                self.stdout.write(
                    self.style.HTTP_INFO(f"ℹ️  Setting exists: {setting_data['key']}")
                )
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"📊 Summary:")
        self.stdout.write(f"   • Created: {created_count} settings")
        self.stdout.write(f"   • Updated: {updated_count} settings")
        self.stdout.write(f"   • Total: {len(default_settings)} settings configured")
        
        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 System settings initialization complete!")
            )
        else:
            self.stdout.write(
                self.style.HTTP_INFO(f"\n✨ All settings already exist. Use --reset to update.")
            )
