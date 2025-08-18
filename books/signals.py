import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from .models import Book
from ai_workflow.src.preprocessors.epub.epub_to_txt_converter import convert_epub_to_txt


@receiver(post_save, sender=Book)
def ensure_txt_conversion(sender, instance: Book, created: bool, **kwargs):
    """
    Ensure that whenever a Book with an EPUB file is saved, a TXT version is
    generated and stored in `txt_file` if it does not already exist.
    """
    try:
        if not instance.file:
            return

        # Ensure source EPUB exists on disk
        if not hasattr(instance.file, 'path') or not os.path.exists(instance.file.path):
            return

        # If txt_file already exists and is present on disk, skip
        if instance.txt_file and hasattr(instance.txt_file, 'path') and os.path.exists(instance.txt_file.path):
            return

        # Convert and save into storage
        txt_path = convert_epub_to_txt(instance.file.path)
        if not os.path.exists(txt_path):
            return

        with open(txt_path, 'r', encoding='utf-8') as f:
            txt_content = f.read()

        # Build filename for storage; storage backend will apply upload_to
        base_name = os.path.splitext(os.path.basename(instance.file.name))[0]
        # Pass a plain .txt name; upload_to will append "_converted.txt"
        target_name = f"{base_name}.txt"

        instance.txt_file.save(target_name, ContentFile(txt_content), save=False)
        instance.save(update_fields=['txt_file', 'updated_at'])

    except Exception:
        # Be conservative: do not raise exceptions from signals
        return


