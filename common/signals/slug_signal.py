from django.db.models.signals import pre_save
from django.dispatch import receiver
from common.utils.slugify import generate_unique_slug


def auto_generate_slug(model, source_field, slug_field="slug"):
    """

    Registers a pre_save signal for the given model to auto-generate a unique slug
    based on a specified field.


    Args:
        model: The model class to which the slug generation should be applied.
        source_field: The field of the instance to base the slug on.
        slug_field: The field in the model where the slug is stored (default is 'slug').
    """

    @receiver(pre_save, sender=model)
    def _slug_handler(sender, instance, **kwargs):
        regenerate = False

        if not instance.pk:
            regenerate = True

        else:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                if getattr(old_instance, source_field) != getattr(
                    instance, source_field
                ):
                    regenerate = True
            except sender.DoesNotExist:
                regenerate = True

        if regenerate or not getattr(instance, slug_field, None):
            generate_unique_slug(
                instance, model, source_field=source_field, slug_field=slug_field
            )
