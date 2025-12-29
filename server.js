const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'frontend')));

const exams = [
  {
    id: 1,
    patientName: 'Maria Silva',
    status: 'Aguardando Laudo',
    fileName: 'ecg_maria.pdf',
    createdAt: new Date().toISOString(),
  },
  {
    id: 2,
    patientName: 'João Pereira',
    status: 'Laudo Disponível',
    fileName: 'ecg_joao.pdf',
    createdAt: new Date().toISOString(),
  },
];

app.get('/exames', (req, res) => {
  res.json(exams);
});

app.post('/exames', (req, res) => {
  const { patientName, fileName } = req.body;

  if (!patientName) {
    return res.status(400).json({ message: 'Nome do paciente é obrigatório.' });
  }

  const exam = {
    id: exams.length + 1,
    patientName,
    fileName: fileName || 'Arquivo não enviado',
    status: 'Aguardando Laudo',
    createdAt: new Date().toISOString(),
  };

  exams.push(exam);
  res.status(201).json(exam);
});

app.get('/clinica/dashboard', (_req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'clinica', 'dashboard', 'index.html'));
});

app.get('/clinica/dashboard/', (_req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'clinica', 'dashboard', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Servidor executando na porta ${PORT}`);
});
