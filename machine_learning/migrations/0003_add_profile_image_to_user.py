from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('machine_learning', '0002_servicecard'),
        ('auth', '0012_alter_user_first_name_max_length'),  # latest auth migration
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE auth_user
            ADD COLUMN profile_image VARCHAR(100) DEFAULT 'profile_pics/default-avatar.png';
            """
        ),
    ]
