import requests
import sys
import json
from datetime import datetime, timedelta

class PaymentAuditAPITester:
    def __init__(self, base_url="https://payment-audit-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/")
            success = response.status_code == 200 and "Payment Operations Audit System" in response.text
            self.log_test("Root Endpoint", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Root Endpoint", False, str(e))
            return False

    def test_get_incidents(self):
        """Test fetching all incidents"""
        try:
            response = requests.get(f"{self.api_url}/incidents")
            success = response.status_code == 200
            if success:
                incidents = response.json()
                success = len(incidents) == 20  # Should have 20 seeded incidents
                self.log_test("Get Incidents", success, f"Found {len(incidents)} incidents (expected 20)")
                return incidents if success else []
            else:
                self.log_test("Get Incidents", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Get Incidents", False, str(e))
            return []

    def test_get_incident_by_id(self, incident_id):
        """Test fetching specific incident"""
        try:
            response = requests.get(f"{self.api_url}/incidents/{incident_id}")
            success = response.status_code == 200
            if success:
                incident = response.json()
                success = incident.get("incident_id") == incident_id
            self.log_test("Get Incident by ID", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Get Incident by ID", False, str(e))
            return False

    def test_create_audit(self, incident_id):
        """Test creating/fetching audit for incident"""
        try:
            response = requests.post(f"{self.api_url}/audits?incident_id={incident_id}")
            success = response.status_code == 200
            if success:
                audit = response.json()
                success = audit.get("incident_id") == incident_id and "audit_id" in audit
                self.log_test("Create/Fetch Audit", success, f"Audit ID: {audit.get('audit_id', 'None')}")
                return audit.get("audit_id") if success else None
            else:
                self.log_test("Create/Fetch Audit", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create/Fetch Audit", False, str(e))
            return None

    def test_get_audit_details(self, audit_id):
        """Test fetching audit details"""
        try:
            response = requests.get(f"{self.api_url}/audits/{audit_id}")
            success = response.status_code == 200
            if success:
                audit_data = response.json()
                required_keys = ["audit", "incident", "checklist", "findings", "actions"]
                success = all(key in audit_data for key in required_keys)
                self.log_test("Get Audit Details", success, f"Keys present: {list(audit_data.keys())}")
                return audit_data if success else None
            else:
                self.log_test("Get Audit Details", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Audit Details", False, str(e))
            return None

    def test_update_checklist(self, audit_data):
        """Test updating checklist items"""
        if not audit_data or not audit_data.get("checklist"):
            self.log_test("Update Checklist", False, "No checklist data available")
            return False

        try:
            checklist_item = audit_data["checklist"][0]  # Get first checklist item
            checklist_id = checklist_item["checklist_id"]
            
            response = requests.post(f"{self.api_url}/checklist", json={
                "checklist_id": checklist_id,
                "response": "yes",
                "evidence_link": "test-evidence-link"
            })
            success = response.status_code == 200
            self.log_test("Update Checklist", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Update Checklist", False, str(e))
            return False

    def test_create_finding(self, audit_id):
        """Test creating a new finding"""
        try:
            response = requests.post(f"{self.api_url}/findings", json={
                "audit_id": audit_id,
                "category": "process_gap",
                "description": "Test finding for automated testing",
                "severity": "medium",
                "evidence_reference": "Test evidence reference"
            })
            success = response.status_code == 200
            if success:
                finding = response.json()
                success = "finding_id" in finding
                self.log_test("Create Finding", success, f"Finding ID: {finding.get('finding_id', 'None')}")
                return finding.get("finding_id") if success else None
            else:
                self.log_test("Create Finding", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create Finding", False, str(e))
            return None

    def test_create_action(self, finding_id, audit_id):
        """Test creating action item"""
        try:
            due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            response = requests.post(f"{self.api_url}/actions", json={
                "finding_id": finding_id,
                "audit_id": audit_id,
                "action_description": "Test action item for automated testing",
                "owner_team": "Engineering",
                "due_date": due_date
            })
            success = response.status_code == 200
            if success:
                action = response.json()
                success = "action_id" in action
                self.log_test("Create Action", success, f"Action ID: {action.get('action_id', 'None')}")
                return action.get("action_id") if success else None
            else:
                self.log_test("Create Action", False, f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Create Action", False, str(e))
            return None

    def test_update_action_status(self, action_id):
        """Test updating action status"""
        try:
            response = requests.post(f"{self.api_url}/actions/update", json={
                "action_id": action_id,
                "status": "completed"
            })
            success = response.status_code == 200
            self.log_test("Update Action Status", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Update Action Status", False, str(e))
            return False

    def test_validate_audit(self, audit_id):
        """Test audit validation"""
        try:
            response = requests.post(f"{self.api_url}/validate", json={
                "audit_id": audit_id,
                "validation_notes": "Test validation for automated testing",
                "validated_by": "Test Validator"
            })
            success = response.status_code == 200
            self.log_test("Validate Audit", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Validate Audit", False, str(e))
            return False

    def test_close_audit_workflow_enforcement(self, audit_id):
        """Test close audit workflow enforcement"""
        try:
            # First try to close without meeting requirements
            response = requests.post(f"{self.api_url}/close-audit?audit_id={audit_id}")
            
            # Should fail initially due to workflow requirements
            if response.status_code == 400:
                self.log_test("Close Audit - Workflow Enforcement", True, "Correctly blocked incomplete audit")
                return True
            else:
                self.log_test("Close Audit - Workflow Enforcement", False, f"Expected 400, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Close Audit - Workflow Enforcement", False, str(e))
            return False

    def test_close_audit_success(self, audit_id):
        """Test successful audit closure after meeting all requirements"""
        try:
            response = requests.post(f"{self.api_url}/close-audit?audit_id={audit_id}")
            success = response.status_code == 200
            if success:
                result = response.json()
                success = result.get("success") == True
            self.log_test("Close Audit - Success", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Close Audit - Success", False, str(e))
            return False

    def run_full_test_suite(self):
        """Run complete test suite"""
        print("🚀 Starting Payment Operations Audit System API Tests")
        print("=" * 60)

        # Test basic endpoints
        if not self.test_root_endpoint():
            print("❌ Root endpoint failed - stopping tests")
            return False

        # Test incidents
        incidents = self.test_get_incidents()
        if not incidents:
            print("❌ No incidents found - stopping tests")
            return False

        # Test specific incident
        test_incident = incidents[0]
        incident_id = test_incident["incident_id"]
        
        if not self.test_get_incident_by_id(incident_id):
            print("❌ Get incident by ID failed")

        # Test audit creation
        audit_id = self.test_create_audit(incident_id)
        if not audit_id:
            print("❌ Audit creation failed - stopping workflow tests")
            return False

        # Test audit details
        audit_data = self.test_get_audit_details(audit_id)
        if not audit_data:
            print("❌ Get audit details failed")
            return False

        # Test checklist update
        self.test_update_checklist(audit_data)

        # Test workflow enforcement (should fail initially)
        self.test_close_audit_workflow_enforcement(audit_id)

        # Test finding creation
        finding_id = self.test_create_finding(audit_id)
        if finding_id:
            # Test action creation
            action_id = self.test_create_action(finding_id, audit_id)
            if action_id:
                # Test action status update
                self.test_update_action_status(action_id)

        # Test validation
        self.test_validate_audit(audit_id)

        # Test successful audit closure (should work now)
        self.test_close_audit_success(audit_id)

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed - check details above")
            return False

def main():
    tester = PaymentAuditAPITester()
    success = tester.run_full_test_suite()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())