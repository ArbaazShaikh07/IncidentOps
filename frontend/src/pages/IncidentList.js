import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IncidentList = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchIncidents();
  }, []);

  const fetchIncidents = async () => {
    try {
      const response = await axios.get(`${API}/incidents`);
      setIncidents(response.data);
    } catch (error) {
      console.error("Error fetching incidents:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewAudit = async (incident) => {
    try {
      const response = await axios.post(`${API}/audits?incident_id=${incident.incident_id}`);
      navigate(`/audit/${response.data.audit_id}`);
    } catch (error) {
      console.error("Error creating/fetching audit:", error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return <div className="loading">Loading incidents...</div>;
  }

  return (
    <div>
      <div className="header">
        <div className="container">
          <h1>Payment Operations Audit System</h1>
          <p>Internal Tool - Incident Management & Audit Tracking</p>
        </div>
      </div>

      <div className="container">
        <div className="table-container">
          <table data-testid="incidents-table">
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Type</th>
                <th>Detected At</th>
                <th>Bank</th>
                <th>Payment Method</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((incident) => (
                <tr key={incident.incident_id} data-testid={`incident-row-${incident.incident_id}`}>
                  <td>{incident.incident_id.substring(0, 8)}...</td>
                  <td>{incident.incident_type.replace("_", " ")}</td>
                  <td>{formatDate(incident.detected_at)}</td>
                  <td>{incident.affected_bank}</td>
                  <td>{incident.payment_method}</td>
                  <td>
                    <span className={`status-badge severity-${incident.severity}`}>
                      {incident.severity}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge status-${incident.status}`}>
                      {incident.status.replace("_", " ")}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleViewAudit(incident)}
                      data-testid={`view-audit-btn-${incident.incident_id}`}
                    >
                      View Audit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default IncidentList;
