# Shingoki Solver

Веб-приложение для решения головоломки «Семафоры» (Shingoki).

## Технологии

- **Backend** — Python, FastAPI, OR-Tools CP-SAT
- **Frontend** — Vue 3, TypeScript, Tailwind CSS, Vite

## Запуск

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Сервер: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Приложение: `http://localhost:5173`
