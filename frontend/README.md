# TruthStream Frontend

React + TypeScript + Vite frontend for TruthStream.

Quick start:

1. cd frontend
2. npm install
3. npm run dev (opens at http://localhost:5173)

The app expects the backend at http://localhost:8000 with endpoint POST /api/v1/verify/ accepting `file` form-data and returning the InvestigationResult JSON.

Design notes:
- Tailwind CSS with custom 0g colors
- Drag/drop + Verify flow
- Loading animation is shown for at least 3s to surface steps
