from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Laboratorio, Semestre, Horario, Agendamento
from .forms import LaboratorioForm, SemestreForm, AgendamentoForm
from datetime import date, time, timedelta

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            messages.error(request, 'Acesso restrito ao administrador.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    if request.session.get('is_admin'):
        return redirect('laboratorio_list')
    return redirect('agendamento_create')


# ===== Laboratório =====

@admin_required
def laboratorio_list(request):
    laboratorios = Laboratorio.objects.all()
    form = LaboratorioForm()
    return render(request, 'agendamento/laboratorio_list.html', {
        'laboratorios': laboratorios,
        'form': form,
        'active_page': 'laboratorio',
    })


@admin_required
def laboratorio_create(request):
    if request.method == 'POST':
        form = LaboratorioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Laboratório cadastrado com sucesso!')
            return redirect('laboratorio_list')
        else:
            laboratorios = Laboratorio.objects.all()
            return render(request, 'agendamento/laboratorio_list.html', {
                'laboratorios': laboratorios,
                'form': form,
                'active_page': 'laboratorio',
            })
    return redirect('laboratorio_list')


@admin_required
def laboratorio_edit(request, pk):
    lab = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        form = LaboratorioForm(request.POST, instance=lab)
        if form.is_valid():
            form.save()
            messages.success(request, 'Laboratório atualizado com sucesso!')
            return redirect('laboratorio_list')
    else:
        form = LaboratorioForm(instance=lab)
    laboratorios = Laboratorio.objects.all()
    return render(request, 'agendamento/laboratorio_list.html', {
        'laboratorios': laboratorios,
        'form': form,
        'edit_lab': lab,
        'active_page': 'laboratorio',
    })


@admin_required
def laboratorio_delete(request, pk):
    lab = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        lab.delete()
        messages.success(request, 'Laboratório excluído com sucesso!')
    return redirect('laboratorio_list')


# ===== Semestre =====

@admin_required
def semestre_list(request):
    semestres = Semestre.objects.all()
    form = SemestreForm()
    return render(request, 'agendamento/semestre_list.html', {
        'semestres': semestres,
        'form': form,
        'active_page': 'semestre',
    })


@admin_required
def semestre_create(request):
    if request.method == 'POST':
        form = SemestreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semestre cadastrado com sucesso!')
            return redirect('semestre_list')
        else:
            semestres = Semestre.objects.all()
            return render(request, 'agendamento/semestre_list.html', {
                'semestres': semestres,
                'form': form,
                'active_page': 'semestre',
            })
    return redirect('semestre_list')


@admin_required
def semestre_edit(request, pk):
    sem = get_object_or_404(Semestre, pk=pk)
    if request.method == 'POST':
        form = SemestreForm(request.POST, instance=sem)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semestre atualizado com sucesso!')
            return redirect('semestre_list')
    else:
        form = SemestreForm(instance=sem)
    semestres = Semestre.objects.all()
    return render(request, 'agendamento/semestre_list.html', {
        'semestres': semestres,
        'form': form,
        'edit_sem': sem,
        'active_page': 'semestre',
    })


@admin_required
def semestre_delete(request, pk):
    sem = get_object_or_404(Semestre, pk=pk)
    if request.method == 'POST':
        sem.delete()
        messages.success(request, 'Semestre excluído com sucesso!')
    return redirect('semestre_list')


# ===== Agendamento =====

def agendamento_create(request):
    # Deleta agendamentos únicos passados e semestres concluídos
    Agendamento.objects.filter(tipo='unico', data_unica__lt=date.today()).delete()
    Agendamento.objects.filter(tipo='semestral', semestre__data_fim__lt=date.today()).delete()

    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agendamento criado com sucesso!')
            return redirect('agendamento_create')
    else:
        form = AgendamentoForm()

    lab_id = request.GET.get('lab')
    sem_id = request.GET.get('sem')
    data_ref_str = request.GET.get('data_ref')
    
    # Defaults
    if not lab_id:
        first_lab = Laboratorio.objects.first()
        if first_lab:
            lab_id = str(first_lab.pk)
            
    target_date = None
    if data_ref_str:
        try:
            target_date = date.fromisoformat(data_ref_str)
        except ValueError:
            pass

    week_dates = {}
    week_headers = {
        1: 'SEGUNDA',
        2: 'TERÇA',
        3: 'QUARTA',
        4: 'QUINTA',
        5: 'SEXTA',
        6: 'SÁBADO'
    }
    
    if target_date:
        current_sem = Semestre.objects.filter(data_inicio__lte=target_date, data_fim__gte=target_date).first()
        if current_sem:
            sem_id = str(current_sem.pk)
        else:
            sem_id = None
        
        weekday = target_date.weekday()
        monday_date = target_date - timedelta(days=weekday) if weekday < 6 else target_date + timedelta(days=1)
        for i in range(6):
            d = monday_date + timedelta(days=i)
            week_dates[i + 1] = d
            week_headers[i + 1] = f"{week_headers[i + 1]} ({d.strftime('%d/%m')})"
    else:
        if not sem_id:
            current_sem = Semestre.objects.filter(data_inicio__lte=date.today(), data_fim__gte=date.today()).first()
            if not current_sem:
                current_sem = Semestre.objects.first()
            if current_sem:
                sem_id = str(current_sem.pk)

    ocupados = {}
    if lab_id:
        # 1. Semestral bookings
        if sem_id:
            agends_sem = Agendamento.objects.filter(laboratorio_id=lab_id, semestre_id=sem_id, tipo='semestral')
            for ag in agends_sem:
                for h in ag.horarios.all():
                    ocupados[(h.dia, h.hora_inicio.strftime('%H:%M'))] = ag.nome

        # 2. Unico bookings inside target date's week
        if target_date and week_dates:
            start_date = week_dates[1]
            end_date = week_dates[6]
            agends_uni = Agendamento.objects.filter(laboratorio_id=lab_id, tipo='unico', data_unica__range=(start_date, end_date))
            for ag in agends_uni:
                for h in ag.horarios.all():
                    if h.dia == ag.data_unica.weekday() + 1:
                        ocupados[(h.dia, h.hora_inicio.strftime('%H:%M'))] = f"{ag.nome} (Avulso)"

    def build_rows(horarios_list):
        rows = []
        for inicio, fim in horarios_list:
            row = {'label': f"{inicio.strftime('%H:%M')} ÀS {fim.strftime('%H:%M')}", 'dias': []}
            for dia in range(1, 7):
                nome = ocupados.get((dia, inicio.strftime('%H:%M')), 'livre')
                row['dias'].append(nome)
            rows.append(row)
        return rows

    manha_times = [(time(8, 0), time(8, 50)), (time(8, 50), time(9, 40)), (time(9, 40), time(10, 30)), (time(10, 45), time(11, 35)), (time(11, 35), time(12, 25)), (time(12, 25), time(13, 0))]
    tarde_times = [(time(14, 0), time(14, 50)), (time(14, 50), time(15, 40)), (time(15, 40), time(16, 30)), (time(16, 45), time(17, 35)), (time(17, 35), time(18, 30))]
    noite_times = [(time(18, 30), time(19, 20)), (time(19, 20), time(20, 10)), (time(20, 10), time(21, 0)), (time(21, 15), time(22, 5)), (time(22, 5), time(22, 55))]

    turnos_grid = {
        'manha': build_rows(manha_times),
        'tarde': build_rows(tarde_times),
        'noite': build_rows(noite_times),
    }

    context = {
        'form': form,
        'agendamentos': Agendamento.objects.all().order_by('-criado_em')[:15],
        'turnos': turnos_grid,
        'active_page': 'agendamento',
        'laboratorios': Laboratorio.objects.all(),
        'semestres': Semestre.objects.all(),
        'sel_lab': lab_id,
        'sel_sem': sem_id,
        'sel_data_ref': data_ref_str or '',
        'week_headers': week_headers,
    }
    return render(request, 'agendamento/agendamento_form.html', context)


def solicitacao_list(request):
    if not request.session.get('is_admin'):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('agendamento_create')
    solicitacoes = Agendamento.objects.filter(solicitou_exclusao=True).order_by('-criado_em')
    return render(request, 'agendamento/solicitacao_list.html', {
        'solicitacoes': solicitacoes,
        'active_page': 'solicitacao',
    })

def solicitacao_aceitar(request, pk):
    if not request.session.get('is_admin'):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('agendamento_create')
    ag = get_object_or_404(Agendamento, pk=pk, solicitou_exclusao=True)
    ag.delete()
    messages.success(request, 'Solicitação aceita e agendamento removido.')
    return redirect('solicitacao_list')

def solicitacao_rejeitar(request, pk):
    if not request.session.get('is_admin'):
        messages.error(request, 'Acesso restrito ao administrador.')
        return redirect('agendamento_create')
    ag = get_object_or_404(Agendamento, pk=pk, solicitou_exclusao=True)
    ag.solicitou_exclusao = False
    ag.save()
    messages.info(request, 'Solicitação rejeitada. Agendamento permanece ativo.')
    return redirect('solicitacao_list')




def agendamento_delete(request, pk):
    ag = get_object_or_404(Agendamento, pk=pk)
    if request.session.get('is_admin'):
        ag.delete()
        messages.success(request, 'Agendamento excluído com sucesso!')
    else:
        ag.solicitou_exclusao = True
        ag.save()
        messages.info(request, 'Solicitação de exclusão enviada. Um administrador irá analisar.')
    return redirect('agendamento_create')


def admin_login(request):
    if request.method == 'POST':
        senha = request.POST.get('senha')
        if senha == 'admin123':
            request.session['is_admin'] = True
            messages.success(request, 'Acesso administrativo liberado!')
            return redirect('laboratorio_list')
        else:
            messages.error(request, 'Senha incorreta!')
    return render(request, 'agendamento/admin_login.html')


def admin_logout(request):
    request.session['is_admin'] = False
    messages.success(request, 'Acesso administrativo encerrado.')
    return redirect('agendamento_create')
