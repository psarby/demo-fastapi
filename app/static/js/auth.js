const tokenKey = "token";
const flashKey = "flash";

function tokenPayload(token) {
   try {
      return JSON.parse(atob(token.split(".")[1]));
   } catch {
      return null;
   }
}

export function getToken() {
   return localStorage.getItem(tokenKey);
}

export function setToken(token) {
   localStorage.setItem(tokenKey, token);
}

export function clearToken() {
   localStorage.removeItem(tokenKey);
}

export function isTokenExpired(token) {
   const payload = tokenPayload(token);
   if (!payload || !payload.exp) {
      return true;
   }

   return payload.exp * 1000 <= Date.now();
}

export function requireAuth() {
   const token = getToken();
   if (!token || isTokenExpired(token)) {
      clearToken();
      setFlash("Session expired. Please login again.", "error");
      window.location.href = "/login";
      return null;
   }

   return token;
}

export function logout(message = "You have been logged out.") {
   clearToken();
   setFlash(message, "success");
   window.location.href = "/login";
}

export function setFlash(message, type = "success") {
   sessionStorage.setItem(flashKey, JSON.stringify({ message, type }));
}

export function showFlash(message, type = "success") {
   const flash = document.querySelector("[data-flash]");
   if (!flash || !message) {
      return;
   }

   flash.textContent = message;
   flash.className = `toast ${type}`;
   flash.hidden = false;

   window.setTimeout(() => {
      flash.hidden = true;
   }, 3500);
}

function consumeFlash() {
   const rawFlash = sessionStorage.getItem(flashKey);
   if (!rawFlash) {
      return;
   }

   sessionStorage.removeItem(flashKey);

   try {
      const flash = JSON.parse(rawFlash);
      showFlash(flash.message, flash.type);
   } catch {
      showFlash(rawFlash);
   }
}

function updateNav() {
   const token = getToken();
   const authenticated = Boolean(token && !isTokenExpired(token));

   if (token && !authenticated) {
      clearToken();
   }

   document.querySelectorAll("[data-auth-link]").forEach((item) => {
      const mode = item.dataset.authLink;
      item.hidden = mode === "user" ? !authenticated : authenticated;
   });
}

async function handleLogin(form) {
   const message = form.querySelector("[data-form-message]");
   const formData = new FormData(form);

   message.textContent = "";

   const response = await fetch("/api/user-login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
         username: formData.get("username").trim(),
         password: formData.get("password"),
      }),
   });

   const data = await response.json();

   if (data.access_token) {
      setToken(data.access_token);
      setFlash("Welcome back.", "success");
      window.location.href = "/dashboard";
      return;
   }

   message.textContent = data.detail || data.error || "Login failed.";
}

async function handleRegister(form) {
   const message = form.querySelector("[data-form-message]");
   const formData = new FormData(form);

   message.textContent = "";

   const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
         username: formData.get("username").trim(),
         password: formData.get("password"),
      }),
   });

   const data = await response.json();

   if (data.id) {
      setFlash("Account created. You can login now.", "success");
      window.location.href = "/login";
      return;
   }

   message.textContent = data.detail || data.error || "Registration failed.";
}

document.addEventListener("DOMContentLoaded", () => {
   consumeFlash();
   updateNav();

   document.querySelectorAll("[data-logout]").forEach((button) => {
      button.addEventListener("click", () => logout());
   });

   const authForm = document.querySelector("[data-auth-form]");
   if (!authForm) {
      return;
   }

   const token = getToken();
   if (token && !isTokenExpired(token)) {
      window.location.href = "/dashboard";
      return;
   }

   authForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const mode = authForm.dataset.authForm;

      try {
         if (mode === "login") {
            await handleLogin(authForm);
         } else {
            await handleRegister(authForm);
         }
      } catch {
         const message = authForm.querySelector("[data-form-message]");
         message.textContent = "Request failed. Please try again.";
      }
   });
});
