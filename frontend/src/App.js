import { BrowserRouter, Routes, Route } from "react-router-dom";
import IncidentList from "./pages/IncidentList";
import AuditDetail from "./pages/AuditDetail";
import "./App.css";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<IncidentList />} />
          <Route path="/audit/:auditId" element={<AuditDetail />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
