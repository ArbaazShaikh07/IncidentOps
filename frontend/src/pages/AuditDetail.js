import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuditDetail = () => {
  const { auditId } = useParams();
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: "", text: "" });

  const [newFinding, setNewFinding] = useState({
    category: "process_gap",
    description: "",
    severity: "medium",
    evidence_reference: "",
  });

  const [newAction, setNewAction] = useState({
    finding_id: "",
    action_description: "",
    owner_team: "Bank Ops",
    due_date: "",
  });

  const [validationForm, setValidationForm] = useState({
    validation_notes: "",
    validated_by: "",
  });

  useEffect(() => {
    fetchAuditData();
  }, [auditId]);

  const fetchAuditData = async () => {
    try {
      const response = await axios.get(`${API}/audits/${auditId}`);
      setAuditData(response.data);
    } catch (error) {
      console.error("Error fetching audit data:", error);
      setMessage({ type: "error", text: "Failed to load audit data" });
    } finally {
      setLoading(false);
    }
  };

  const updateChecklistItem = async (checklistId, response, evidenceLink) => {
    try {
      await axios.post(`${API}/checklist`, {
        checklist_id: checklistId,
        response: response,
        evidence_link: evidenceLink || "",
      });
      fetchAuditData();
      setMessage({ type: "success", text: "Checklist updated" });
      setTimeout(() => setMessage({ type: "", text: "" }), 3000);
    } catch (error) {
      console.error("Error updating checklist:", error);
      setMessage({ type: "error", text: "Failed to update checklist" });
    }
  };

  const addFinding = async (e) => {
    e.preventDefault();
    if (!newFinding.description) {
      setMessage({ type: "error", text: "Description is required" });
      return;
    }

    try {
      await axios.post(`${API}/findings`, {
        audit_id: auditId,
        ...newFinding,
      });
      setNewFinding({
        category: "process_gap",
        description: "",
        severity: "medium",
        evidence_reference: "",
      });
      fetchAuditData();
      setMessage({ type: "success", text: "Finding added" });
      setTimeout(() => setMessage({ type: "", text: "" }), 3000);
    } catch (error) {
      console.error("Error adding finding:", error);
      setMessage({ type: "error", text: "Failed to add finding" });
    }
  };

  const addAction = async (e) => {
    e.preventDefault();
    if (!newAction.finding_id || !newAction.action_description || !newAction.due_date) {
      setMessage({ type: "error", text: "All action fields are required" });
      return;
    }

    try {
      await axios.post(`${API}/actions`, {
        ...newAction,
        audit_id: auditId,
      });
      setNewAction({
        finding_id: "",
        action_description: "",
        owner_team: "Bank Ops",
        due_date: "",
      });
      fetchAuditData();
      setMessage({ type: "success", text: "Action item added" });
      setTimeout(() => setMessage({ type: "", text: "" }), 3000);
    } catch (error) {
      console.error("Error adding action:", error);
      setMessage({ type: "error", text: "Failed to add action" });
    }
  };

  const updateActionStatus = async (actionId, status) => {
    try {
      await axios.post(`${API}/actions/update`, {
        action_id: actionId,
        status: status,
      });
      fetchAuditData();
      setMessage({ type: "success", text: "Action status updated" });
      setTimeout(() => setMessage({ type: "", text: "" }), 3000);
    } catch (error) {
      console.error("Error updating action:", error);
      setMessage({ type: "error", text: "Failed to update action" });
    }
  };

  const submitValidation = async (e) => {
    e.preventDefault();
    if (!validationForm.validation_notes || !validationForm.validated_by) {
      setMessage({ type: "error", text: "All validation fields are required" });
      return;
    }

    try {
      await axios.post(`${API}/validate`, {
        audit_id: auditId,
        ...validationForm,
      });
      fetchAuditData();
      setMessage({ type: "success", text: "Validation submitted" });
      setTimeout(() => setMessage({ type: "", text: "" }), 3000);
    } catch (error) {
      console.error("Error submitting validation:", error);
      setMessage({ type: "error", text: "Failed to submit validation" });
    }
  };

  const closeAudit = async () => {
    try {
      await axios.post(`${API}/close-audit?audit_id=${auditId}`);
      fetchAuditData();
      setMessage({ type: "success", text: "Audit closed successfully" });
    } catch (error) {
      console.error("Error closing audit:", error);
      const errorMsg = error.response?.data?.detail || "Failed to close audit";
      setMessage({ type: "error", text: errorMsg });
    }
  };

  const canCloseAudit = () => {
    if (!auditData) return false;
    if (auditData.audit.audit_status === "closed") return false;

    const allChecklistCompleted = auditData.checklist.every(
      (item) => item.response !== "pending"
    );
    const hasFindings = auditData.findings.length > 0;
    const allActionsCompleted = auditData.actions.every(
      (action) => action.status === "completed"
    );
    const validationDone = auditData.validation && auditData.validation.validation_done;

    return allChecklistCompleted && hasFindings && allActionsCompleted && validationDone;
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
    return <div className="loading">Loading audit data...</div>;
  }

  if (!auditData) {
    return <div className="empty-state">Audit not found</div>;
  }

  return (
    <div>
      <div className="header">
        <div className="container">
          <h1>Audit Case Detail</h1>
          <p>Audit ID: {auditId}</p>
        </div>
      </div>

      <div className="container">
        <Link to="/" className="back-link" data-testid="back-to-incidents-link">
          ← Back to Incidents
        </Link>

        {message.text && (
          <div className={`alert alert-${message.type}`} data-testid="alert-message">
            {message.text}
          </div>
        )}

        <div className="section" data-testid="incident-details-section">
          <h2>Incident Details</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Incident Type</span>
              <span className="info-value">
                {auditData.incident.incident_type.replace("_", " ")}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Detected At</span>
              <span className="info-value">{formatDate(auditData.incident.detected_at)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Bank</span>
              <span className="info-value">{auditData.incident.affected_bank}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Payment Method</span>
              <span className="info-value">{auditData.incident.payment_method}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Severity</span>
              <span className={`status-badge severity-${auditData.incident.severity}`}>
                {auditData.incident.severity}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Status</span>
              <span className={`status-badge status-${auditData.incident.status}`}>
                {auditData.incident.status.replace("_", " ")}
              </span>
            </div>
          </div>
        </div>

        <div className="section" data-testid="audit-info-section">
          <h2>Audit Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Audit Owner</span>
              <span className="info-value">{auditData.audit.audit_owner}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Start Date</span>
              <span className="info-value">{formatDate(auditData.audit.audit_start_date)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Audit Status</span>
              <span className={`status-badge status-${auditData.audit.audit_status}`}>
                {auditData.audit.audit_status.replace("_", " ")}
              </span>
            </div>
          </div>
        </div>

        <div className="section" data-testid="checklist-section">
          <h2>Audit Checklist</h2>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Question</th>
                  <th>Response</th>
                  <th>Evidence Link</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {auditData.checklist.map((item) => (
                  <tr key={item.checklist_id} data-testid={`checklist-item-${item.checklist_id}`}>
                    <td>{item.question}</td>
                    <td>
                      <span className={`status-badge status-${item.response}`}>
                        {item.response.replace("_", " ")}
                      </span>
                    </td>
                    <td>{item.evidence_link || "-"}</td>
                    <td>
                      {auditData.audit.audit_status !== "closed" && (
                        <select
                          value={item.response}
                          onChange={(e) =>
                            updateChecklistItem(item.checklist_id, e.target.value, item.evidence_link)
                          }
                          data-testid={`checklist-response-${item.checklist_id}`}
                        >
                          <option value="pending">Pending</option>
                          <option value="yes">Yes</option>
                          <option value="no">No</option>
                          <option value="not_applicable">Not Applicable</option>
                        </select>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="section" data-testid="findings-section">
          <h2>Audit Findings</h2>
          {auditData.findings.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Category</th>
                    <th>Description</th>
                    <th>Severity</th>
                    <th>Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {auditData.findings.map((finding) => (
                    <tr key={finding.finding_id} data-testid={`finding-${finding.finding_id}`}>
                      <td>{finding.category.replace("_", " ")}</td>
                      <td>{finding.description}</td>
                      <td>
                        <span className={`status-badge severity-${finding.severity}`}>
                          {finding.severity}
                        </span>
                      </td>
                      <td>{finding.evidence_reference || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No findings yet.</p>
          )}

          {auditData.audit.audit_status !== "closed" && (
            <form onSubmit={addFinding} data-testid="add-finding-form">
              <h3>Add New Finding</h3>
              <div className="form-group">
                <label>Category</label>
                <select
                  value={newFinding.category}
                  onChange={(e) => setNewFinding({ ...newFinding, category: e.target.value })}
                  data-testid="finding-category-select"
                >
                  <option value="process_gap">Process Gap</option>
                  <option value="tech_issue">Tech Issue</option>
                  <option value="bank_issue">Bank Issue</option>
                  <option value="monitoring_gap">Monitoring Gap</option>
                </select>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newFinding.description}
                  onChange={(e) => setNewFinding({ ...newFinding, description: e.target.value })}
                  data-testid="finding-description-input"
                />
              </div>
              <div className="form-group">
                <label>Severity</label>
                <select
                  value={newFinding.severity}
                  onChange={(e) => setNewFinding({ ...newFinding, severity: e.target.value })}
                  data-testid="finding-severity-select"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div className="form-group">
                <label>Evidence Reference</label>
                <input
                  type="text"
                  value={newFinding.evidence_reference}
                  onChange={(e) =>
                    setNewFinding({ ...newFinding, evidence_reference: e.target.value })
                  }
                  data-testid="finding-evidence-input"
                />
              </div>
              <button type="submit" className="btn btn-primary" data-testid="add-finding-btn">
                Add Finding
              </button>
            </form>
          )}
        </div>

        <div className="section" data-testid="actions-section">
          <h2>Action Items</h2>
          {auditData.actions.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Owner Team</th>
                    <th>Due Date</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {auditData.actions.map((action) => (
                    <tr key={action.action_id} data-testid={`action-${action.action_id}`}>
                      <td>{action.action_description}</td>
                      <td>{action.owner_team}</td>
                      <td>{formatDate(action.due_date)}</td>
                      <td>
                        <span className={`status-badge status-${action.status}`}>
                          {action.status.replace("_", " ")}
                        </span>
                      </td>
                      <td>
                        {auditData.audit.audit_status !== "closed" && (
                          <select
                            value={action.status}
                            onChange={(e) => updateActionStatus(action.action_id, e.target.value)}
                            data-testid={`action-status-${action.action_id}`}
                          >
                            <option value="open">Open</option>
                            <option value="in_progress">In Progress</option>
                            <option value="completed">Completed</option>
                          </select>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No action items yet.</p>
          )}

          {auditData.audit.audit_status !== "closed" && auditData.findings.length > 0 && (
            <form onSubmit={addAction} data-testid="add-action-form">
              <h3>Add New Action Item</h3>
              <div className="form-group">
                <label>Finding</label>
                <select
                  value={newAction.finding_id}
                  onChange={(e) => setNewAction({ ...newAction, finding_id: e.target.value })}
                  data-testid="action-finding-select"
                >
                  <option value="">Select a finding</option>
                  {auditData.findings.map((finding) => (
                    <option key={finding.finding_id} value={finding.finding_id}>
                      {finding.description.substring(0, 50)}...
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Action Description</label>
                <textarea
                  value={newAction.action_description}
                  onChange={(e) =>
                    setNewAction({ ...newAction, action_description: e.target.value })
                  }
                  data-testid="action-description-input"
                />
              </div>
              <div className="form-group">
                <label>Owner Team</label>
                <select
                  value={newAction.owner_team}
                  onChange={(e) => setNewAction({ ...newAction, owner_team: e.target.value })}
                  data-testid="action-owner-select"
                >
                  <option value="Bank Ops">Bank Ops</option>
                  <option value="Engineering">Engineering</option>
                  <option value="Product">Product</option>
                </select>
              </div>
              <div className="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  value={newAction.due_date}
                  onChange={(e) => setNewAction({ ...newAction, due_date: e.target.value })}
                  data-testid="action-due-date-input"
                />
              </div>
              <button type="submit" className="btn btn-primary" data-testid="add-action-btn">
                Add Action Item
              </button>
            </form>
          )}
        </div>

        <div className="section" data-testid="closure-section">
          <h2>Closure & Validation</h2>

          {auditData.validation ? (
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Validated By</span>
                <span className="info-value">{auditData.validation.validated_by}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Validated At</span>
                <span className="info-value">
                  {formatDate(auditData.validation.validated_at)}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Validation Notes</span>
                <span className="info-value">{auditData.validation.validation_notes}</span>
              </div>
            </div>
          ) : (
            auditData.audit.audit_status !== "closed" && (
              <form onSubmit={submitValidation} data-testid="validation-form">
                <div className="form-group">
                  <label>Validated By</label>
                  <input
                    type="text"
                    value={validationForm.validated_by}
                    onChange={(e) =>
                      setValidationForm({ ...validationForm, validated_by: e.target.value })
                    }
                    data-testid="validation-by-input"
                  />
                </div>
                <div className="form-group">
                  <label>Validation Notes</label>
                  <textarea
                    value={validationForm.validation_notes}
                    onChange={(e) =>
                      setValidationForm({ ...validationForm, validation_notes: e.target.value })
                    }
                    data-testid="validation-notes-input"
                  />
                </div>
                <button type="submit" className="btn btn-secondary" data-testid="submit-validation-btn">
                  Submit Validation
                </button>
              </form>
            )
          )}

          <div
            className={`audit-status-indicator ${canCloseAudit() ? "can-close" : "cannot-close"}`}
            data-testid="audit-status-indicator"
          >
            {auditData.audit.audit_status === "closed" ? (
              <strong>Audit Status: CLOSED</strong>
            ) : canCloseAudit() ? (
              <strong>Ready to close: All requirements met</strong>
            ) : (
              <div>
                <strong>Cannot close audit. Requirements:</strong>
                <ul style={{ marginTop: "10px", paddingLeft: "20px" }}>
                  <li>
                    All checklist items completed:{" "
                    {auditData.checklist.every((item) => item.response !== "pending")
                      ? "✓"
                      : "✗"}
                  </li>
                  <li>At least one finding: {auditData.findings.length > 0 ? "✓" : "✗"}</li>
                  <li>
                    All action items completed:{" "
                    {auditData.actions.every((action) => action.status === "completed")
                      ? "✓"
                      : "✗"}
                  </li>
                  <li>
                    Closure validation done:{" "
                    {auditData.validation && auditData.validation.validation_done ? "✓" : "✗"}
                  </li>
                </ul>
              </div>
            )}
          </div>

          {auditData.audit.audit_status !== "closed" && (
            <button
              className="btn btn-success"
              onClick={closeAudit}
              disabled={!canCloseAudit()}
              data-testid="close-audit-btn"
            >
              Close Audit
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuditDetail;
