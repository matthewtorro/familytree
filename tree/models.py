from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('U', 'Неизвестно'),
    ]

    # Разграничение доступа: дерево принадлежит конкретному пользователю
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец дерева")

    # Основные анкетные данные
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U', verbose_name="Пол")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    death_date = models.DateField(null=True, blank=True, verbose_name="Дата смерти")

    # Рекурсивные связи (Связь модели на саму себя)
    father = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children_from_father', 
        verbose_name="Отец"
    )
    mother = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children_from_mother', 
        verbose_name="Мать"
    )
    spouse = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='+', 
        verbose_name="Супруг / Супруга"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """
        Кастомная валидация данных (биологический абсурд и проверка пола)
        """
        super().clean()

        # 1. Проверка пола родителей
        if self.father and self.father.gender == 'F':
            raise ValidationError({'father': "Отец не может быть женского пола."})
        
        if self.mother and self.mother.gender == 'M':
            raise ValidationError({'mother': "Мать не может быть мужского пола."})

        # 2. Проверка дат (нельзя родиться после смерти)
        if self.birth_date and self.death_date and self.birth_date > self.death_date:
            raise ValidationError({'death_date': "Дата смерти не может быть раньше даты рождения."})

        # 3. Базовая проверка разницы в возрасте с родителями (не менее 12 лет)
        if self.birth_date:
            if self.father and self.father.birth_date:
                if (self.birth_date - self.father.birth_date).days < 12 * 365:
                    raise ValidationError({'father': "Отец слишком молод, чтобы быть родителем (разница менее 12 лет)."})
            
            if self.mother and self.mother.birth_date:
                if (self.birth_date - self.mother.birth_date).days < 12 * 365:
                    raise ValidationError({'mother': "Мать слишком молода, чтобы быть родителем (разница менее 12 лет)."})