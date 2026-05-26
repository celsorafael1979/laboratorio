from django.db import models

class Laboratorio(models.Model):
    nome = models.CharField('Nome', max_length=200)
    local = models.CharField('Local', max_length=200)
    responsavel = models.CharField('Responsável', max_length=200)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Laboratório'
        verbose_name_plural = 'Laboratórios'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Semestre(models.Model):
    SEMESTRE_CHOICES = [
        (1, '1º Semestre'),
        (2, '2º Semestre'),
    ]

    ano = models.IntegerField('Ano')
    semestre = models.IntegerField('Semestre', choices=SEMESTRE_CHOICES)
    data_inicio = models.DateField('Data Inicial')
    data_fim = models.DateField('Data Final')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Semestre'
        verbose_name_plural = 'Semestres'
        ordering = ['-ano', '-semestre']
        unique_together = ['ano', 'semestre']

    def __str__(self):
        return f"{self.ano}/{self.semestre}º"


class Horario(models.Model):
    DIA_CHOICES = [
        (1, 'Segunda'),
        (2, 'Terça'),
        (3, 'Quarta'),
        (4, 'Quinta'),
        (5, 'Sexta'),
        (6, 'Sábado'),
    ]
    TURNO_CHOICES = [
        ('M', 'Manhã'),
        ('T', 'Tarde'),
        ('N', 'Noite'),
    ]
    dia = models.IntegerField('Dia da Semana', choices=DIA_CHOICES)
    turno = models.CharField('Turno', max_length=1, choices=TURNO_CHOICES, default='M')
    hora_inicio = models.TimeField('Hora Início')
    hora_fim = models.TimeField('Hora Fim')

    class Meta:
        verbose_name = 'Horário'
        verbose_name_plural = 'Horários'
        ordering = ['dia', 'hora_inicio']
        unique_together = ['dia', 'hora_inicio']

    def __str__(self):
        return f"{self.get_dia_display()} - {self.hora_inicio:%H:%M} às {self.hora_fim:%H:%M}"


class Agendamento(models.Model):
    TIPO_CHOICES = [
        ('unico', 'Um dia específico'),
        ('semestral', 'Durante todo o semestre')
    ]

    laboratorio = models.ForeignKey(Laboratorio, verbose_name='Laboratório', on_delete=models.CASCADE, related_name='agendamentos')
    semestre = models.ForeignKey(Semestre, verbose_name='Semestre', on_delete=models.SET_NULL, null=True, blank=True, related_name='agendamentos')
    horarios = models.ManyToManyField(Horario, verbose_name='Horários', related_name='agendamentos')
    solicitou_exclusao = models.BooleanField('Solicitou Exclusão', default=False)

    nome = models.CharField('Nome', max_length=200)
    colegiado = models.CharField('Colegiado', max_length=200, blank=True, null=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    tipo = models.CharField('Tipo de Agendamento', max_length=10, choices=TIPO_CHOICES, default='unico')
    data_unica = models.DateField('Data (única)', blank=True, null=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)



    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-criado_em']

    def __str__(self):
        if self.tipo == 'unico':
            return f"{self.nome} - {self.laboratorio.nome} - {self.data_unica}"
        return f"{self.nome} - {self.laboratorio.nome} - Semestral"
