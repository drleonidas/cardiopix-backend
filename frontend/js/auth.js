const AUTH_ENDPOINT = '/api/auth/login';
const STORAGE_KEY = 'cardiopix:user';

const statusEl = document.getElementById('status');
const formEl = document.getElementById('login-form');

const showStatus = (message, isError = false) => {
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.classList.toggle('error', isError);
};

const persistSession = (payload) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
};

const redirectByProfile = (profile) => {
  if (profile === 'ADMIN/CLINICA') {
    window.location.href = '/frontend/dashboard-clinica.html';
    return;
  }

  window.location.href = '/frontend/fila-laudos.html';
};

const mockAuthenticate = async ({ email, password, profile }) => {
  await new Promise((resolve) => setTimeout(resolve, 280));

  if (!email || !password || !profile) {
    throw new Error('Preencha todos os campos para continuar.');
  }

  return {
    token: 'mock-token',
    user: {
      email,
      profile,
    },
  };
};

const authenticate = async (payload) => {
  try {
    const response = await fetch(AUTH_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error('Credenciais inválidas.');
    }

    return response.json();
  } catch (error) {
    return mockAuthenticate(payload);
  }
};

if (formEl) {
  formEl.addEventListener('submit', async (event) => {
    event.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const profile = document.getElementById('profile').value;

    showStatus('Autenticando...');

    try {
      const result = await authenticate({ email, password, profile });
      persistSession(result.user);
      showStatus('Login realizado com sucesso! Redirecionando...');
      redirectByProfile(result.user.profile);
    } catch (error) {
      showStatus(error.message || 'Não foi possível fazer login agora.', true);
    }
  });
}
