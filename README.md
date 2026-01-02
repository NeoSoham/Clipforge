# ⚽ ClipForge

**ClipForge** is an AI-assisted football gameplay highlight generator that automatically detects goals and creates cinematic highlight clips with build-up, goal, and celebration.

Built with a **Python + FastAPI backend** and a **React + Vite + Tailwind frontend**, ClipForge turns raw gameplay footage into shareable highlights in minutes.

---

## ✨ Features

- 🎯 Automatic goal detection using motion analysis  
- 🎬 Story-style clips (build-up → goal → celebration)  
- 🖼️ Auto-generated thumbnails  
- 📊 Match analytics (goals, durations, total highlight time)  
- ⌨️ Keyboard navigation (← → Esc)  
- 🧭 Interactive timeline with markers  
- 🌐 Full-stack web interface  

---

## 🧠 How It Works

1. Video is uploaded via the web UI
2. Backend extracts frames & audio
3. Motion heuristics detect high-intensity events
4. Goal windows are expanded into story clips
5. Clips + thumbnails are generated
6. Metadata & analytics are returned to the frontend

---

## 🛠 Tech Stack

### Backend
- Python
- FastAPI
- OpenCV
- NumPy
- Librosa
- FFmpeg

### Frontend
- React
- Vite
- Tailwind CSS
- Framer Motion

---

## 📂 Project Structure

ClipForge/
├── api/ # FastAPI application
├── engine/ # Core video processing logic
├── web/ # Frontend (React + Vite)
├── requirements.txt
├── runtime.txt
└── README.md

---

## 🚀 Running Locally

### Backend
```
pip install -r requirements.txt
uvicorn api.app:app --reload
```

### Frontend

```
cd web
npm install
npm run dev
```

## Deployment

- Backend: Railway/Render
- Frontend: Vercel/Netlify

## 🧑‍💻 Author

Built with ❤️ and a lot of late-night debugging.
