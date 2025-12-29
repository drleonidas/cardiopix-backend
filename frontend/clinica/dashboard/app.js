const modal = document.getElementById('modal-exame');
const novoExameBtn = document.getElementById('novo-exame');
const fecharModalBtn = document.getElementById('fechar-modal');
const cancelarBtn = document.getElementById('cancelar');
const formExame = document.getElementById('form-exame');
const listaExames = document.getElementById('exames-lista');
const recarregarBtn = document.getElementById('recarregar');
const uploadName = document.getElementById('upload-name');
const inputFile = document.getElementById('ecg-file');
const simularBtn = document.getElementById('simular-anexo');

let simulatedFileName = null;

function toggleModal(open) {
  if (open) {
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
  } else {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    formExame.reset();
    simulatedFileName = null;
    uploadName.textContent = 'Nenhum arquivo selecionado';
  }
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function buildStatusBadge(status) {
  const badge = document.createElement('span');
  badge.classList.add('badge');

  const normalized = status.toLowerCase();
  if (normalized.includes('aguardando')) {
    badge.classList.add('badge--pending');
  } else {
    badge.classList.add('badge--ready');
  }

  badge.textContent = status;
  return badge;
}

function renderExams(exams = []) {
  if (!exams.length) {
    listaExames.innerHTML = '<p class="muted">Nenhum exame cadastrado ainda.</p>';
    return;
  }

  const header = ['Paciente', 'Arquivo', 'Status', 'Criado em'];
  const headerRow = header
    .map((title) => `<div class="table__header">${title}</div>`)
    .join('');

  const rows = exams
    .map((exam) => {
      return `
        <div class="table__row">
          <div>
            <p class="strong">${exam.patientName}</p>
            <p class="muted">ID #${exam.id}</p>
          </div>
          <div>
            <p class="muted">${exam.fileName || 'Arquivo não enviado'}</p>
          </div>
          <div>${buildStatusBadge(exam.status).outerHTML}</div>
          <div class="muted">${formatDate(exam.createdAt)}</div>
        </div>
      `;
    })
    .join('');

  listaExames.innerHTML = headerRow + rows;
}

async function carregarExames() {
  listaExames.innerHTML = '<p class="muted">Carregando exames...</p>';
  try {
    const response = await fetch('/exames');
    const data = await response.json();
    renderExams(data);
  } catch (error) {
    console.error(error);
    listaExames.innerHTML = '<p class="muted">Erro ao carregar exames.</p>';
  }
}

async function salvarExame(event) {
  event.preventDefault();
  const formData = new FormData(formExame);
  const patientName = formData.get('patientName');
  const fileName = inputFile.files[0]?.name || simulatedFileName;

  if (!patientName) {
    alert('Informe o nome do paciente.');
    return;
  }

  try {
    const response = await fetch('/exames', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patientName, fileName }),
    });

    if (!response.ok) {
      const error = await response.json();
      alert(error.message || 'Não foi possível salvar o exame.');
      return;
    }

    await carregarExames();
    toggleModal(false);
  } catch (error) {
    console.error(error);
    alert('Falha ao comunicar com o servidor.');
  }
}

novoExameBtn.addEventListener('click', () => toggleModal(true));
fecharModalBtn.addEventListener('click', () => toggleModal(false));
cancelarBtn.addEventListener('click', () => toggleModal(false));
recarregarBtn.addEventListener('click', carregarExames);
formExame.addEventListener('submit', salvarExame);

inputFile.addEventListener('change', (event) => {
  const file = event.target.files[0];
  simulatedFileName = null;
  uploadName.textContent = file ? file.name : 'Nenhum arquivo selecionado';
});

simularBtn.addEventListener('click', () => {
  simulatedFileName = 'ECG_simulado.pdf';
  inputFile.value = '';
  uploadName.textContent = simulatedFileName;
});

carregarExames();
