from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models


UF_CHOICES = [
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
]


class Clinica(models.Model):
    nome = models.CharField(max_length=255)
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(r"^\d{14}$", "CNPJ deve conter 14 dígitos numéricos.")],
    )
    endereco_completo = models.TextField()
    logomarca_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.razao_social


class Medico(models.Model):
    nome = models.CharField(max_length=255)
    crm_numero = models.CharField(
        max_length=10,
        validators=[RegexValidator(r"^\d+$", "CRM deve conter apenas números.")],
    )
    uf_crm = models.CharField(max_length=2, choices=UF_CHOICES)
    rqe = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\d*$", "RQE deve conter apenas números.")],
    )
    foto_perfil_url = models.URLField(blank=True)
    crm_documento_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.nome


class PacienteManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Usuários devem ter um endereço de e-mail")
        email = self.normalize_email(email)
        cpf = extra_fields.get("cpf")
        if not cpf:
            raise ValueError("Usuários devem ter um CPF")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Paciente(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField("nome", max_length=150, blank=True)
    last_name = models.CharField("sobrenome", max_length=150, blank=True)
    email = models.EmailField(unique=True)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(r"^\d{11}$", "CPF deve conter 11 dígitos numéricos.")],
    )
    data_nascimento = models.DateField()
    telefone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                r"^[+]?\d{8,20}$",
                "Telefone deve conter apenas dígitos, podendo incluir prefixo +.",
            )
        ],
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["cpf"]

    objects = PacienteManager()

    def __str__(self) -> str:
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
