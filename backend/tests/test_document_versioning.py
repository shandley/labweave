"""Tests for document versioning functionality."""
import pytest
import os
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from src.main import app
from src.models.user import User
from src.models.project import Project
from src.models.document import Document


def test_upload_document_with_version_info(client: TestClient, test_user_token: str, test_project: Project):
    """Test uploading a document creates version 1."""
    test_file_content = b"Test FASTQ content"
    test_file = ("test.fastq", test_file_content, "text/plain")
    
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": test_file},
        data={
            "title": "Test FASTQ File",
            "description": "A test sequencing file",
            "project_id": test_project.id,
            "document_type": "sequencing_data",
            "tags": "test,fastq"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    
    # Verify the document has version info
    doc_response = client.get(
        f"/documents/{data['id']}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert doc_response.status_code == 200
    doc_data = doc_response.json()
    assert doc_data["version_number"] == 1
    assert doc_data["is_latest"] is True
    assert doc_data["parent_document_id"] is None
    assert doc_data["file_hash"] is not None


def test_upload_new_version(client: TestClient, test_user_token: str, test_project: Project):
    """Test uploading a new version of a document."""
    # First upload original document
    test_file_content = b"Original content"
    test_file = ("test.txt", test_file_content, "text/plain")
    
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": test_file},
        data={
            "title": "Test Document",
            "project_id": test_project.id
        }
    )
    
    assert response.status_code == 200
    original_id = response.json()["id"]
    
    # Upload new version
    new_content = b"Updated content"
    new_file = ("test_v2.txt", new_content, "text/plain")
    
    version_response = client.post(
        f"/documents/{original_id}/versions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": new_file},
        data={
            "version_comment": "Updated analysis parameters"
        }
    )
    
    assert version_response.status_code == 200
    version_data = version_response.json()
    
    assert version_data["version_number"] == 2
    assert version_data["is_latest"] is True
    assert version_data["parent_document_id"] == original_id
    assert version_data["version_comment"] == "Updated analysis parameters"
    
    # Check original is no longer latest
    original_response = client.get(
        f"/documents/{original_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    original_data = original_response.json()
    assert original_data["is_latest"] is False
    assert original_data["version_number"] == 1


def test_get_document_versions(client: TestClient, test_user_token: str, test_project: Project):
    """Test retrieving all versions of a document."""
    # Create document with multiple versions
    test_file = ("test.txt", b"Version 1", "text/plain")
    
    # Upload original
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": test_file},
        data={"title": "Multi-version doc", "project_id": test_project.id}
    )
    
    doc_id = response.json()["id"]
    
    # Upload two more versions
    for i in range(2, 4):
        new_file = ("test.txt", f"Version {i}".encode(), "text/plain")
        client.post(
            f"/documents/{doc_id}/versions",
            headers={"Authorization": f"Bearer {test_user_token}"},
            files={"file": new_file},
            data={"version_comment": f"Update {i}"}
        )
    
    # Get all versions
    versions_response = client.get(
        f"/documents/{doc_id}/versions",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert versions_response.status_code == 200
    versions = versions_response.json()
    
    assert len(versions) == 3
    assert [v["version_number"] for v in versions] == [1, 2, 3]
    assert versions[-1]["is_latest"] is True
    assert all(not v["is_latest"] for v in versions[:-1])


def test_restore_document_version(client: TestClient, test_user_token: str, test_project: Project):
    """Test restoring an old version of a document."""
    # Create document with versions
    original_content = b"Original content"
    test_file = ("test.txt", original_content, "text/plain")
    
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": test_file},
        data={"title": "Test restore", "project_id": test_project.id}
    )
    
    doc_id = response.json()["id"]
    
    # Upload new version
    new_file = ("test.txt", b"Modified content", "text/plain")
    client.post(
        f"/documents/{doc_id}/versions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": new_file}
    )
    
    # Restore version 1
    restore_response = client.post(
        f"/documents/{doc_id}/restore/1",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert restore_response.status_code == 200
    restored = restore_response.json()
    
    assert restored["version_number"] == 3
    assert restored["is_latest"] is True
    assert "Restored from version 1" in restored["version_comment"]
    
    # Verify file content matches original
    download_response = client.get(
        f"/documents/{restored['id']}/download",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert download_response.status_code == 200
    assert download_response.content == original_content


def test_delete_document_cascade(client: TestClient, test_user_token: str, test_project: Project):
    """Test deleting all versions of a document."""
    # Create document with versions
    test_file = ("test.txt", b"Content", "text/plain")
    
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": test_file},
        data={"title": "Test delete", "project_id": test_project.id}
    )
    
    doc_id = response.json()["id"]
    
    # Add version
    client.post(
        f"/documents/{doc_id}/versions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        files={"file": test_file}
    )
    
    # Delete with cascade
    delete_response = client.delete(
        f"/documents/{doc_id}?cascade=true",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert delete_response.status_code == 200
    assert "2 document(s)" in delete_response.json()["detail"]
    
    # Verify all versions are gone
    versions_response = client.get(
        f"/documents/{doc_id}/versions",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert versions_response.status_code == 404


def test_filter_latest_documents(client: TestClient, test_user_token: str, test_project: Project):
    """Test filtering for only latest versions of documents."""
    # Create multiple documents with versions
    for i in range(2):
        test_file = ("test.txt", f"Doc {i}".encode(), "text/plain")
        
        response = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {test_user_token}"},
            files={"file": test_file},
            data={"title": f"Doc {i}", "project_id": test_project.id}
        )
        
        doc_id = response.json()["id"]
        
        # Add a version
        client.post(
            f"/documents/{doc_id}/versions",
            headers={"Authorization": f"Bearer {test_user_token}"},
            files={"file": ("test.txt", f"Doc {i} v2".encode(), "text/plain")}
        )
    
    # Get only latest versions
    latest_response = client.get(
        f"/documents/?project_id={test_project.id}&latest_only=true",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert latest_response.status_code == 200
    latest_docs = latest_response.json()
    
    assert len(latest_docs) == 2
    assert all(doc["is_latest"] for doc in latest_docs)
    assert all(doc["version_number"] == 2 for doc in latest_docs)
    
    # Get all versions
    all_response = client.get(
        f"/documents/?project_id={test_project.id}&latest_only=false",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    all_docs = all_response.json()
    assert len(all_docs) == 4  # 2 documents × 2 versions each