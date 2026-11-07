def test_create_and_list_tasks(client):
    created = client.post("/tasks", json={"title": "Learn GCP", "description": "Module 3"})
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Learn GCP"
    assert body["completed"] is False
    task_id = body["id"]

    listed = client.get("/tasks")
    assert listed.status_code == 200
    ids = [t["id"] for t in listed.json()]
    assert task_id in ids


def test_update_task_marks_completed(client):
    created = client.post("/tasks", json={"title": "Ship feature"})
    task_id = created.json()["id"]

    updated = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Temporary"})
    task_id = created.json()["id"]

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/tasks/{task_id}")
    assert missing.status_code == 404


def test_task_stats(client):
    client.post("/tasks", json={"title": "A"})
    task_b = client.post("/tasks", json={"title": "B"}).json()
    client.patch(f"/tasks/{task_b['id']}", json={"completed": True})

    stats = client.get("/tasks/stats")
    assert stats.status_code == 200
    data = stats.json()
    assert data["total"] == 2
    assert data["completed"] == 1
    assert data["open"] == 1
    assert data["completion_rate"] == 50.0
