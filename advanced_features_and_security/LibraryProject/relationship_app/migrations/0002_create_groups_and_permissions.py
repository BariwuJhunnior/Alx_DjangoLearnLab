from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Get the content type for Book model
    try:
        book_ct = ContentType.objects.get(app_label='relationship_app', model='book')
    except ContentType.DoesNotExist:
        return

    # Codenames defined on Book model
    codenames = ['can_view', 'can_create', 'can_edit', 'can_delete']
    perms = Permission.objects.filter(content_type=book_ct, codename__in=codenames)

    # Create groups
    viewers, _ = Group.objects.get_or_create(name='Viewers')
    editors, _ = Group.objects.get_or_create(name='Editors')
    admins, _ = Group.objects.get_or_create(name='Admins')

    # Assign permissions
    for p in perms:
        if p.codename == 'can_view':
            viewers.permissions.add(p)
            editors.permissions.add(p)
            admins.permissions.add(p)
        if p.codename in ('can_create', 'can_edit'):
            editors.permissions.add(p)
            admins.permissions.add(p)
        if p.codename == 'can_delete':
            admins.permissions.add(p)


def reverse_func(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Viewers', 'Editors', 'Admins']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('relationship_app', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_func),
    ]
