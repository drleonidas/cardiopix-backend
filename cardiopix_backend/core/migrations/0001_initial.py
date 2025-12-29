from django.db import migrations, models
import django.core.validators
import cardiopix_backend.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Clinica",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=255)),
                ("razao_social", models.CharField(max_length=255)),
                (
                    "cnpj",
                    models.CharField(
                        max_length=14,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^\\d{14}$", "CNPJ deve conter 14 dígitos numéricos."
                            )
                        ],
                    ),
                ),
                ("endereco_completo", models.TextField()),
                ("logomarca_url", models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Medico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=255)),
                (
                    "crm_numero",
                    models.CharField(
                        max_length=10,
                        validators=[django.core.validators.RegexValidator("^\\d+$", "CRM deve conter apenas números.")],
                    ),
                ),
                (
                    "uf_crm",
                    models.CharField(
                        choices=[
                            ("AC", "Acre"),
                            ("AL", "Alagoas"),
                            ("AP", "Amapá"),
                            ("AM", "Amazonas"),
                            ("BA", "Bahia"),
                            ("CE", "Ceará"),
                            ("DF", "Distrito Federal"),
                            ("ES", "Espírito Santo"),
                            ("GO", "Goiás"),
                            ("MA", "Maranhão"),
                            ("MT", "Mato Grosso"),
                            ("MS", "Mato Grosso do Sul"),
                            ("MG", "Minas Gerais"),
                            ("PA", "Pará"),
                            ("PB", "Paraíba"),
                            ("PR", "Paraná"),
                            ("PE", "Pernambuco"),
                            ("PI", "Piauí"),
                            ("RJ", "Rio de Janeiro"),
                            ("RN", "Rio Grande do Norte"),
                            ("RS", "Rio Grande do Sul"),
                            ("RO", "Rondônia"),
                            ("RR", "Roraima"),
                            ("SC", "Santa Catarina"),
                            ("SP", "São Paulo"),
                            ("SE", "Sergipe"),
                            ("TO", "Tocantins"),
                        ],
                        max_length=2,
                    ),
                ),
                (
                    "rqe",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        validators=[django.core.validators.RegexValidator("^\\d*$", "RQE deve conter apenas números.")],
                    ),
                ),
                ("foto_perfil_url", models.URLField(blank=True)),
                ("crm_documento_url", models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Paciente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "password",
                    models.CharField(max_length=128, verbose_name="password"),
                ),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="nome")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="sobrenome")),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "cpf",
                    models.CharField(
                        max_length=11,
                        unique=True,
                        validators=[django.core.validators.RegexValidator("^\\d{11}$", "CPF deve conter 11 dígitos numéricos.")],
                    ),
                ),
                ("data_nascimento", models.DateField()),
                (
                    "telefone",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[+]?\\d{8,20}$",
                                "Telefone deve conter apenas dígitos, podendo incluir prefixo +.",
                            )
                        ],
                    ),
                ),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("objects", cardiopix_backend.core.models.PacienteManager()),
            ],
        ),
    ]
