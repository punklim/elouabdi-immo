from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("biens", "0003_avis"),
    ]

    operations = [
        migrations.AddField(
            model_name="demande",
            name="note_interne",
            field=models.TextField(blank=True, default="", verbose_name="Note interne"),
        ),
    ]