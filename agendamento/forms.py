from django import forms
from .models import Laboratorio, Semestre, Horario, Agendamento
from datetime import date

class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorio
        fields = ['nome', 'local', 'responsavel']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SemestreForm(forms.ModelForm):
    class Meta:
        model = Semestre
        fields = ['ano', 'semestre', 'data_inicio', 'data_fim']
        widgets = {
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        if data_inicio and data_fim and data_fim <= data_inicio:
            raise forms.ValidationError('A data final deve ser posterior à data inicial.')
        return cleaned_data

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['laboratorio', 'nome', 'colegiado', 'telefone', 'tipo', 'data_unica', 'semestre', 'horarios']
        widgets = {
            'laboratorio': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'colegiado': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'data_unica': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'semestre': forms.Select(attrs={'class': 'form-select'}),
            'horarios': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_unica'].widget.attrs['min'] = date.today().isoformat()
        self.fields['colegiado'].required = True
        self.fields['telefone'].required = True

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
        data = cleaned.get('data_unica')
        semestre = cleaned.get('semestre')
        horarios = cleaned.get('horarios')
        laboratorio = cleaned.get('laboratorio')

        if tipo == 'unico' and not data:
            self.add_error('data_unica', 'Data única é obrigatória para este tipo.')
        if tipo == 'semestral' and not semestre:
            self.add_error('semestre', 'Obrigatório escolher o Semestre para agendamento semestral.')

        if tipo == 'unico' and data and horarios and laboratorio:
            if data < date.today():
                raise forms.ValidationError('Não é permitido realizar agendamentos em datas passadas.')

            # Encontre o semestre correspondente à data
            semestre_correspondente = Semestre.objects.filter(data_inicio__lte=data, data_fim__gte=data).first()
            weekday_num = data.weekday() + 1  # 1 (Segunda) a 6 (Sábado), 7 (Domingo)
            
            if weekday_num == 7:
                raise forms.ValidationError('Não é permitido realizar agendamentos aos domingos.')

            for h in horarios:
                # 1. Garante que o horário bate com o dia da semana da data
                if h.dia != weekday_num:
                    raise forms.ValidationError(f'O horário "{h}" não corresponde ao dia da semana da data {data.strftime("%d/%m/%Y")}.')
                
                # 2. Verifica se já existe agendamento único nessa data e horário
                if Agendamento.objects.filter(laboratorio=laboratorio, horarios=h, data_unica=data).exists():
                    raise forms.ValidationError(f'O horário {h.hora_inicio.strftime("%H:%M")} já está reservado nesta data.')
                
                # 3. Verifica se já existe agendamento semestral ocupando esse dia da semana no semestre da data
                if semestre_correspondente:
                    if Agendamento.objects.filter(laboratorio=laboratorio, horarios=h, semestre=semestre_correspondente, tipo='semestral').exists():
                        raise forms.ValidationError(f'O horário {h.hora_inicio.strftime("%H:%M")} já está ocupado por um agendamento semestral neste período.')
                    
        if tipo == 'semestral' and semestre and horarios and laboratorio:
            for h in horarios:
                # 1. Verifica se já existe outro agendamento semestral
                if Agendamento.objects.filter(laboratorio=laboratorio, horarios=h, semestre=semestre, tipo='semestral').exists():
                    raise forms.ValidationError(f'O horário {h} já está reservado de forma semestral para este laboratório no semestre {semestre}.')
                
                # 2. Verifica se já existem agendamentos únicos (avulsos) conflitando dentro das datas deste semestre
                if Agendamento.objects.filter(
                    laboratorio=laboratorio,
                    horarios=h,
                    tipo='unico',
                    data_unica__range=(semestre.data_inicio, semestre.data_fim)
                ).exists():
                    raise forms.ValidationError(f'O horário {h} já possui agendamentos avulsos cadastrados para datas dentro deste semestre.')

        return cleaned
