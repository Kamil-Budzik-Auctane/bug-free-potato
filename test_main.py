import pytest
from fastapi.testclient import TestClient
from main import app
from models import ActionType
import json

client = TestClient(app)


class TestAPI:
    def test_root_endpoint(self):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Shipment Risk Prediction Engine"
        assert "endpoints" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    def test_get_packages(self):
        """Test getting all packages with risk scores"""
        response = client.get("/packages")
        assert response.status_code == 200
        
        packages = response.json()
        assert len(packages) == 5  # We have 5 mock packages
        
        for package in packages:
            assert "package_id" in package
            assert "risk_score" in package
            assert "reasons" in package
            assert 0 <= package["risk_score"] <= 100
            assert isinstance(package["reasons"], list)
    
    def test_get_single_package(self):
        """Test getting single package risk assessment"""
        response = client.get("/packages/PKG001")
        assert response.status_code == 200
        
        package = response.json()
        assert package["package_id"] == "PKG001"
        assert "risk_score" in package
        assert "reasons" in package
    
    def test_get_nonexistent_package(self):
        """Test getting package that doesn't exist"""
        response = client.get("/packages/NONEXISTENT")
        assert response.status_code == 404
    
    def test_send_alert(self):
        """Test sending alert for a package"""
        alert_data = {
            "package_id": "PKG001",
            "customer_email": "test@example.com"
        }
        
        response = client.post("/send-alert", json=alert_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["email_sent"] is True
    
    def test_send_alert_nonexistent_package(self):
        """Test sending alert for nonexistent package"""
        alert_data = {
            "package_id": "NONEXISTENT"
        }
        
        response = client.post("/send-alert", json=alert_data)
        assert response.status_code == 404
    
    def test_log_customer_action(self):
        """Test logging customer action"""
        action_data = {
            "package_id": "PKG001",
            "action": "Accept Delay",
            "customer_id": "CUST123",
            "notes": "Test action"
        }
        
        response = client.post("/action", json=action_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["action_logged"] is True
    
    def test_log_action_nonexistent_package(self):
        """Test logging action for nonexistent package"""
        action_data = {
            "package_id": "NONEXISTENT",
            "action": "Accept Delay"
        }
        
        response = client.post("/action", json=action_data)
        assert response.status_code == 404
    
    def test_get_customer_actions(self):
        """Test getting logged customer actions"""
        # First log an action
        action_data = {
            "package_id": "PKG002",
            "action": "Request Refund"
        }
        client.post("/action", json=action_data)
        
        # Then get actions
        response = client.get("/actions")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_actions" in data
        assert "actions" in data
        assert data["total_actions"] >= 1


if __name__ == "__main__":
    pytest.main([__file__])