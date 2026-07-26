document.addEventListener("DOMContentLoaded", () => {
  console.log("Admin dashboard loaded");
  loadUsers();
  loadDocuments();

  // Tab switching
  document.querySelectorAll(".tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(sec => sec.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });

  // Add user form
  document.getElementById("addUserForm").addEventListener("submit", async e => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const role = document.getElementById("role").value;

    const formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("role", role);

    try {
      const res = await fetch("/admin/users/add", {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        loadUsers();
        e.target.reset();
      } else {
        const err = await res.json();
        alert("Error adding user: " + err.detail);
      }
    } catch (error) {
      console.error("Add user failed:", error);
    }
  });

  // Upload document form
  document.getElementById("uploadForm").addEventListener("submit", async e => {
    e.preventDefault();
    const file = document.getElementById("docFile").files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("uploaded_by", "admin");
    formData.append("lang", "eng+hin+mar+guj+tam+tel+ben+kan+mal+pan+urd");

    try {
      const res = await fetch("/admin/documents/upload", {
        method: "POST",
        body: formData
      });

      const msg = document.getElementById("uploadMsg");
      if (res.ok) {
        const data = await res.json();
        msg.textContent = `Uploaded successfully: ${data.file_id}`;
        loadDocuments();
        e.target.reset();
      } else {
        const err = await res.json();
        msg.textContent = `Error: ${err.detail}`;
      }
    } catch (error) {
      console.error("Upload failed:", error);
    }
  });
});

// ---------------- USERS ----------------
async function loadUsers() {
  try {
    const res = await fetch("/admin/users");
    if (!res.ok) throw new Error("Failed to fetch users");
    const data = await res.json();
    const tbody = document.getElementById("usersBody");
    tbody.innerHTML = "";

    if (data.users && data.users.length > 0) {
      data.users.forEach(user => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${user.name}</td>
          <td>${user.email}</td>
          <td>${user.role}</td>
          <td><button onclick="removeUser('${user.email}')">Remove</button></td>
        `;
        tbody.appendChild(row);
      });
    } else {
      tbody.innerHTML = "<tr><td colspan='4'>No users found</td></tr>";
    }
  } catch (error) {
    console.error("Failed to load users:", error);
  }
}

async function removeUser(email) {
  const formData = new FormData();
  formData.append("email", email);

  try {
    const res = await fetch("/admin/users/remove", {
      method: "DELETE",
      body: formData
    });
    if (res.ok) loadUsers();
  } catch (error) {
    console.error("Remove user failed:", error);
  }
}

// ---------------- DOCUMENTS ----------------
async function loadDocuments() {
  try {
    const res = await fetch("/admin/documents");
    if (!res.ok) throw new Error("Failed to fetch documents");
    const data = await res.json();
    const tbody = document.getElementById("docsBody");
    tbody.innerHTML = "";

    if (data.documents && data.documents.length > 0) {
      data.documents.forEach(doc => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${doc.filename}</td>
          <td>${doc.uploaded_by}</td>
          <td><button onclick="removeDocument('${doc.file_id}')">Delete</button></td>
        `;
        tbody.appendChild(row);
      });
    } else {
      tbody.innerHTML = "<tr><td colspan='3'>No documents found</td></tr>";
    }
  } catch (error) {
    console.error("Failed to load documents:", error);
  }
}

async function removeDocument(file_id) {
  const formData = new FormData();
  formData.append("file_id", file_id);

  try {
    const res = await fetch("/admin/documents/remove", {
      method: "DELETE",
      body: formData
    });
    if (res.ok) loadDocuments();
  } catch (error) {
    console.error("Remove document failed:", error);
  }
}