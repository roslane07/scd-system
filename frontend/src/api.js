/**
 * SCD API Client — Fetch wrapper with JWT auth.
 *
 * All API calls go through this module. It automatically:
 *   - Attaches the JWT token from localStorage
 *   - Redirects to /login on 401 (expired token)
 *   - Returns parsed JSON
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('scd_token');
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem('scd_token');
    localStorage.removeItem('scd_user');
    window.location.href = '/login';
    return null;
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Bousin du tabagn's — réessaie cop's");
  }

  return data;
}

// ── Auth ──────────────────────────────────────────────────
export const login = (nom, email, password) =>
  apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ nom: nom || undefined, email: email || undefined, password }),
  });

export const refreshToken = () => apiFetch('/auth/refresh', { method: 'POST' });

export const changePassword = (old_password, new_password) =>
  apiFetch('/auth/password', {
    method: 'PATCH',
    body: JSON.stringify({ old_password, new_password }),
  });

export const forgotPassword = (email) =>
  apiFetch('/auth/forgot', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });

export const resetPassword = (token, new_password) =>
  apiFetch('/auth/reset', {
    method: 'POST',
    body: JSON.stringify({ token, new_password }),
  });

export const setupProfile = (data) =>
  apiFetch('/auth/setup', {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const getAnciensList = () => apiFetch('/auth/anciens-list');

// ── Conscrits ────────────────────────────────────────────
export const getConscrits = () => apiFetch('/conscrits/');
export const getConscritsByZone = (zone) => apiFetch(`/conscrits/zone/${zone}`);
export const getConscrit = (id) => apiFetch(`/conscrits/${id}`);
export const getHistorique = (id) => apiFetch(`/conscrits/${id}/historique`);
export const getRestrictions = (id) => apiFetch(`/conscrits/${id}/restrictions`);
export const getFam = (id) => apiFetch(`/conscrits/${id}/fam`);
export const getNotifications = (id) => apiFetch(`/conscrits/${id}/notifications`);
export const markNotificationRead = (notifId) =>
  apiFetch(`/conscrits/${notifId}/notification/lu`, { method: 'POST' });

// ── Infractions ──────────────────────────────────────────
export const getInfractionTypes = () => apiFetch('/infractions/types');
export const applyInfraction = (conscrit_id, code, commentaire) =>
  apiFetch('/infractions/apply', {
    method: 'POST',
    body: JSON.stringify({ conscrit_id, code, commentaire }),
  });
export const cancelInfraction = (logId, justification) =>
  apiFetch(`/infractions/cancel/${logId}`, {
    method: 'POST',
    body: JSON.stringify({ justification }),
  });

// ── Classement ───────────────────────────────────────────
export const getClassementIndividuel = () => apiFetch('/classement/individuel');
export const getClassementFams = () => apiFetch('/classement/fams');
export const getStats = () => apiFetch('/classement/stats');

// ── Helpers ──────────────────────────────────────────────
export function getUser() {
  const raw = localStorage.getItem('scd_user');
  return raw ? JSON.parse(raw) : null;
}

export function saveAuth(data) {
  localStorage.setItem('scd_token', data.access_token);
  localStorage.setItem('scd_user', JSON.stringify({
    id: data.id,
    role: data.role,
    nom: data.nom,
    prenom: data.prenom,
    buque: data.buque,
    first_login: data.first_login,
  }));
}

export function logout() {
  localStorage.removeItem('scd_token');
  localStorage.removeItem('scd_user');
  window.location.href = '/login';
}

export function getZoneClass(zone) {
  if (!zone) return '';
  return zone.replace('ZONE_', '').toLowerCase();
}

export function getZoneEmoji(zone) {
  const map = {
    ZONE_VERTE: '🟢',
    ZONE_JAUNE: '🟡',
    ZONE_ORANGE: '🟠',
    ZONE_ROUGE: '🔴',
    ZONE_NOIRE: '⚫',
  };
  return map[zone] || '';
}

export function getZoneLabel(zone) {
  const map = {
    ZONE_VERTE: 'Verte',
    ZONE_JAUNE: 'Jaune',
    ZONE_ORANGE: 'Orange',
    ZONE_ROUGE: 'Rouge',
    ZONE_NOIRE: 'Noire',
  };
  return map[zone] || zone;
}
