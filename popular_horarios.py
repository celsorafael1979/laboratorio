import os
import django
from datetime import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agendamento.models import Horario

def popular_horarios():
    Horario.objects.all().delete()
    
    dias = [1, 2, 3, 4, 5, 6]  # Segunda a Sábado
    
    horarios_manha = [
        (time(8, 0), time(8, 50)),
        (time(8, 50), time(9, 40)),
        (time(9, 40), time(10, 30)),
        (time(10, 45), time(11, 35)),
        (time(11, 35), time(12, 25)),
        (time(12, 25), time(13, 0)),
    ]
    
    horarios_tarde = [
        (time(14, 0), time(14, 50)),
        (time(14, 50), time(15, 40)),
        (time(15, 40), time(16, 30)),
        (time(16, 45), time(17, 35)),
        (time(17, 35), time(18, 30)),
    ]
    
    horarios_noite = [
        (time(18, 30), time(19, 20)),
        (time(19, 20), time(20, 10)),
        (time(20, 10), time(21, 0)),
        (time(21, 15), time(22, 5)),
        (time(22, 5), time(22, 55)),
    ]
    
    criados = 0
    for dia in dias:
        for inicio, fim in horarios_manha:
            Horario.objects.create(dia=dia, turno='M', hora_inicio=inicio, hora_fim=fim)
            criados += 1
            
        for inicio, fim in horarios_tarde:
            Horario.objects.create(dia=dia, turno='T', hora_inicio=inicio, hora_fim=fim)
            criados += 1
            
        for inicio, fim in horarios_noite:
            Horario.objects.create(dia=dia, turno='N', hora_inicio=inicio, hora_fim=fim)
            criados += 1

    print(f"Sucesso! {criados} horários criados na base de dados.")

if __name__ == '__main__':
    popular_horarios()
