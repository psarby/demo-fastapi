import { getToken, logout, requireAuth, showFlash } from "./auth.js";

const token = requireAuth();
const form = document.getElementById("visitor-form");
const message = document.getElementById("form-message");
const list = document.getElementById("visitors-list");
const emptyState = document.getElementById("empty-state");
const refreshButton = document.getElementById("refresh-visitors");
const currentUser = document.querySelector("[data-current-user]");

function authHeaders(includeJson = false) {
   const headers = {
      Authorization: `Bearer ${getToken()}`,
   };

   if (includeJson) {
      headers["Content-Type"] = "application/json";
   }

   return headers;
}

function handleUnauthorized(response) {
   if (response.status === 401) {
      logout("Session expired. Please login again.");
      return true;
   }

   return false;
}

async function loadCurrentUser() {
   const response = await fetch("/api/me", {
      headers: authHeaders(),
   });

   if (handleUnauthorized(response)) {
      return;
   }

   const data = await response.json();

   if (data.username) {
      currentUser.textContent = data.username;
      return;
   }

   currentUser.textContent = "unknown user";
}

function renderVisitors(visitors) {
   list.innerHTML = "";

   if (!Array.isArray(visitors) || visitors.length === 0) {
      emptyState.hidden = false;
      return;
   }

   emptyState.hidden = true;

   visitors.forEach((visitor) => {
      const item = document.createElement("li");
      const name = document.createElement("span");
      const deleteButton = document.createElement("button");

      name.textContent = visitor.name;
      deleteButton.type = "button";
      deleteButton.textContent = "Delete";
      deleteButton.className = "secondary";
      deleteButton.addEventListener("click", () => deleteVisitor(visitor.id));

      item.appendChild(name);
      item.appendChild(deleteButton);
      list.appendChild(item);
   });
}

async function loadVisitors() {
   const response = await fetch("/api/my-visitors", {
      headers: authHeaders(),
   });

   if (handleUnauthorized(response)) {
      return;
   }

   if (!response.ok) {
      showFlash("Failed to load visitors.", "error");
      return;
   }

   renderVisitors(await response.json());
}

async function createVisitor() {
   const nameInput = document.getElementById("visitor-name");
   const name = nameInput.value.trim();

   message.textContent = "";

   if (!name) {
      message.textContent = "Visitor name is required.";
      return;
   }

   const response = await fetch("/api/visitors", {
      method: "POST",
      headers: authHeaders(true),
      body: JSON.stringify({ name }),
   });

   if (handleUnauthorized(response)) {
      return;
   }

   if (!response.ok) {
      message.textContent = "Failed to create visitor.";
      return;
   }

   nameInput.value = "";
   showFlash("Visitor added.", "success");
   await loadVisitors();
}

async function deleteVisitor(id) {
   const response = await fetch(`/api/visitors/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
   });

   if (handleUnauthorized(response)) {
      return;
   }

   if (!response.ok) {
      showFlash("Failed to delete visitor.", "error");
      return;
   }

   showFlash("Visitor deleted.", "success");
   await loadVisitors();
}

if (token) {
   form.addEventListener("submit", async (event) => {
      event.preventDefault();
      await createVisitor();
   });

   refreshButton.addEventListener("click", loadVisitors);

   await loadCurrentUser();
   await loadVisitors();
}
