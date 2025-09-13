from django.utils.text import slugify


def generate_unique_slug(
    instance, model, source_field, slug_field="slug", slugify_func=slugify
):
    """
    Generates a unique slug for a given instance based on the ather field.

    Args:
        instance: The model instance for which to generate the slug.
        model: The model class to check for uniqueness.
        field: The field of the instance to base the slug on (e.g., 'title').
        slug_field: The field in the model where the slug is stored (default is 'slug').
        slugify_func: The function used to create the slug (default is Django's slugify).
    """
    base_value = getattr(instance, source_field)
    if not base_value:
        raise ValueError(f"Cannot generate slug: '{source_field}' is empty.")
    base_slug = slugify_func(base_value)
    slug = base_slug
    unique_suffix = 1

    qs = model.objects.exclude(pk=instance.pk) if instance.pk else model.objects.all()

    while qs.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{unique_suffix}"
        unique_suffix += 1

    setattr(instance, slug_field, slug)
