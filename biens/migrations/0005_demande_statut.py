from django.db import migrations, models


def statut_depuis_traitee(apps, schema_editor):
    """Les demandes déjà traitées gardent leur état : elles passent au statut « Traité »."""
    Demande = apps.get_model("biens", "Demande")
    Demande.objects.filter(traitee=True).update(statut="traitee")


class Migration(migrations.Migration):

    dependencies = [
        ("biens", "0004_demande_note_interne"),
    ]

    operations = [
        migrations.AddField(
            model_name="demande",
            name="statut",
            field=models.CharField(
                choices=[("nouveau", "Nouveau"), ("en_cours", "En cours"), ("traitee", "Traité")],
                default="nouveau",
                max_length=10,
                verbose_name="Statut",
            ),
        ),
        migrations.RunPython(statut_depuis_traitee, migrations.RunPython.noop),
    ]
