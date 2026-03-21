import uuid

import pytest


@pytest.mark.asyncio
async def test_auth_and_users_flow(client, admin_token):
    username = f"it_user_{uuid.uuid4().hex[:8]}"

    create_user_response = await client.post(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"username": username, "password": "password123"},
    )
    assert create_user_response.status_code == 201

    login_response = await client.post(
        "/auth/token",
        json={"username": username, "password": "password123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


@pytest.mark.asyncio
async def test_posts_crud_flow(client, admin_token):
    create_response = await client.post(
        "/posts/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Integration Post",
            "content": "integration content",
            "published": True,
        },
    )
    assert create_response.status_code == 201
    created_post = create_response.json()
    post_id = created_post["id"]

    list_response = await client.get("/posts/?published=true&skip=0&limit=10")
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)

    get_response = await client.get(f"/posts/{post_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == post_id

    patch_response = await client.patch(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Updated Integration Post"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Updated Integration Post"
    assert patch_response.json()["author_id"] > 0

    delete_response = await client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_post_owner_authorization(client, admin_token):
    create_owner_response = await client.post(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"username": f"owner_{uuid.uuid4().hex[:8]}", "password": "password123"},
    )
    assert create_owner_response.status_code == 201

    owner_login = await client.post(
        "/auth/token",
        json={
            "username": create_owner_response.json()["username"],
            "password": "password123",
        },
    )
    owner_token = owner_login.json()["access_token"]

    create_other_response = await client.post(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"username": f"other_{uuid.uuid4().hex[:8]}", "password": "password123"},
    )
    assert create_other_response.status_code == 201

    other_login = await client.post(
        "/auth/token",
        json={
            "username": create_other_response.json()["username"],
            "password": "password123",
        },
    )
    other_token = other_login.json()["access_token"]

    created_post = await client.post(
        "/posts/",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"title": "Owned post", "content": "content", "published": True},
    )
    assert created_post.status_code == 201
    post_id = created_post.json()["id"]

    forbidden_patch = await client.patch(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"title": "hijack"},
    )
    assert forbidden_patch.status_code == 403

    forbidden_delete = await client.delete(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert forbidden_delete.status_code == 403


@pytest.mark.asyncio
async def test_posts_protected_routes_require_token(client):
    response = await client.post(
        "/posts/",
        json={"title": "No token", "content": "blocked", "published": True},
    )
    assert response.status_code == 401
