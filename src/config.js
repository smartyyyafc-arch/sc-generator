const getApiBase = () => {
  if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
  if (process.env.NODE_ENV === 'production') return '/api';
  return 'http://localhost:5000/api';
};

export const API_BASE = getApiBase();

export const ALLOWED_FILE_EXTENSIONS = ['.exe', '.msi', '.dll', '.bat', '.cmd', '.vbs'];
