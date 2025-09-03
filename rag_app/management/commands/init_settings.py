import os
from django.core.management.base import BaseCommand
from rag_app.models import SystemSettings


class Command(BaseCommand):
    """
    Initialize system settings with default values from environment variables.
    Usage: python manage.py init_settings
    """
    help = 'Initialize system settings with default values'

    def handle(self, *args, **options):
        # Default system settings with environment variable overrides
        default_settings = {
            'rag_similarity_threshold': os.getenv('SIMILARITY_THRESHOLD', '0.1'),
            'rag_max_chunks': os.getenv('MAX_CHUNKS_RETURNED', '5'),
            'rag_llm_model': os.getenv('OPENROUTER_DEFAULT_MODEL', 'google/gemini-2.5-flash'),
            'rag_max_context_length': '4000',
            'rag_temperature': '0.7',
            'rag_max_tokens': '1000',
            'rag_include_metadata': 'true',
            'embeddings_model': os.getenv('EMBEDDINGS_MODEL', 'all-mpnet-base-v2'),
            'chunk_size': os.getenv('CHUNK_SIZE', '1000'),
            'chunk_overlap': os.getenv('CHUNK_OVERLAP', '100'),
            'max_file_size_mb': os.getenv('MAX_FILE_SIZE_MB', '5'),
        }

        created_count = 0
        updated_count = 0

        for key, default_value in default_settings.items():
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={'value': default_value}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created setting: {key} = {default_value}')
                )
            else:
                # Update existing setting if environment variable is set
                env_value = None
                if key == 'rag_similarity_threshold':
                    env_value = os.getenv('SIMILARITY_THRESHOLD')
                elif key == 'rag_max_chunks':
                    env_value = os.getenv('MAX_CHUNKS_RETURNED')
                elif key == 'rag_llm_model':
                    env_value = os.getenv('OPENROUTER_DEFAULT_MODEL')
                elif key == 'embeddings_model':
                    env_value = os.getenv('EMBEDDINGS_MODEL')
                elif key == 'chunk_size':
                    env_value = os.getenv('CHUNK_SIZE')
                elif key == 'chunk_overlap':
                    env_value = os.getenv('CHUNK_OVERLAP')
                elif key == 'max_file_size_mb':
                    env_value = os.getenv('MAX_FILE_SIZE_MB')
                
                if env_value and setting.value != env_value:
                    setting.value = env_value
                    setting.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated setting: {key} = {env_value}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Existing setting: {key} = {setting.value}')
                    )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'✅ Settings initialization complete!')
        )
        self.stdout.write(f'   📝 Created: {created_count} settings')
        self.stdout.write(f'   🔄 Updated: {updated_count} settings')
        self.stdout.write(f'   📊 Total: {len(default_settings)} settings configured')