(() => {
    "use strict";

    const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;
    const RELOAD_CHECK_INTERVAL_MS = 1200;
    const UI_PREFS_KEY = "taskflow_ui_prefs_v1";

    class ToastService {
        constructor(container) {
            this.container = container;
            this.variantClass = {
                success: "text-bg-success",
                error: "text-bg-danger",
                warning: "text-bg-warning",
                info: "text-bg-primary",
            };
        }

        show({ title, message, variant = "info", delay = 3800 }) {
            const toastElement = document.createElement("div");
            toastElement.className = `toast align-items-center ${this.variantClass[variant] || this.variantClass.info}`;
            toastElement.role = "alert";
            toastElement.ariaLive = "assertive";
            toastElement.ariaAtomic = "true";
            toastElement.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${this.escapeHtml(title)}:</strong> ${this.escapeHtml(message)}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Inchide"></button>
                </div>
            `;

            this.container.appendChild(toastElement);
            const toast = new bootstrap.Toast(toastElement, { delay });
            toast.show();

            toastElement.addEventListener("hidden.bs.toast", () => {
                toastElement.remove();
            });
        }

        escapeHtml(text) {
            const div = document.createElement("div");
            div.textContent = String(text || "");
            return div.innerHTML;
        }
    }

    class AuthStore {
        constructor(storage) {
            this.storage = storage;
            this.tokenKey = "token";
        }

        setToken(token) {
            this.storage.setItem(this.tokenKey, token);
        }

        getToken() {
            return this.storage.getItem(this.tokenKey);
        }

        clearToken() {
            this.storage.removeItem(this.tokenKey);
        }

        getUserEmail() {
            const token = this.getToken();
            if (!token) {
                return "";
            }
            try {
                const payload = JSON.parse(atob(token.split(".")[1]));
                return payload.sub || "";
            } catch {
                return "";
            }
        }
    }

    class ApiClient {
        constructor(baseUrl, authStore) {
            this.baseUrl = baseUrl;
            this.authStore = authStore;
        }

        async request(path, options = {}, withAuth = false) {
            const headers = { ...(options.headers || {}) };

            if (withAuth) {
                const token = this.authStore.getToken();
                if (!token) {
                    throw new Error("Nu esti autentificat.");
                }
                headers.Authorization = `Bearer ${token}`;
            }

            const response = await fetch(`${this.baseUrl}${path}`, {
                ...options,
                headers,
            });

            if (response.status === 204) {
                return null;
            }

            let data = null;
            const contentType = response.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                const message = this.extractErrorMessage(data, response.status);
                const error = new Error(message);
                error.status = response.status;
                throw error;
            }

            return data;
        }

        extractErrorMessage(data, status) {
            if (data && typeof data === "object") {
                if (typeof data.detail === "string") {
                    return data.detail;
                }
                if (data.error && typeof data.error.message === "string") {
                    return data.error.message;
                }
                if (typeof data.message === "string") {
                    return data.message;
                }
            }
            return `Cererea a esuat (status ${status}).`;
        }

        register(email, password) {
            return this.request("/inregistrare", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email.trim(), parola: password }),
            });
        }

        login(email, password) {
            const payload = new URLSearchParams();
            payload.append("username", email.trim());
            payload.append("password", password);
            return this.request("/autentificare", {
                method: "POST",
                body: payload,
            });
        }

        listTasks(unfinishedOnly) {
            const query = unfinishedOnly ? "?doar_nefinalizate=true" : "";
            return this.request(`/sarcini${query}`, { method: "GET" }, true);
        }

        createTask(titlu, descriere) {
            return this.request(
                "/sarcini",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ titlu: titlu.trim(), descriere: descriere.trim() }),
                },
                true,
            );
        }

        updateTask(id, titlu, descriere) {
            return this.request(
                `/sarcini/${id}`,
                {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ titlu: titlu.trim(), descriere: descriere.trim() }),
                },
                true,
            );
        }

        finishTask(id) {
            return this.request(
                `/sarcini/${id}/finalizeaza`,
                {
                    method: "PATCH",
                },
                true,
            );
        }

        deleteTask(id) {
            return this.request(
                `/sarcini/${id}`,
                {
                    method: "DELETE",
                },
                true,
            );
        }

        getWebVersion() {
            return this.request("/web/version", { method: "GET" }, false);
        }
    }

    class TaskApp {
        constructor() {
            this.authStore = new AuthStore(window.localStorage);
            this.api = new ApiClient(API_BASE, this.authStore);
            this.toast = new ToastService(document.getElementById("toast-container"));
            this.state = {
                tasks: [],
                editingTaskId: null,
                loading: false,
                latestWebVersion: null,
            };

            this.dom = {
                authSection: document.getElementById("auth-section"),
                tasksSection: document.getElementById("tasks-section"),
                userControls: document.getElementById("user-controls"),
                userEmail: document.getElementById("user-email"),
                addTaskModal: document.getElementById("addTaskModal"),
                btnLogout: document.getElementById("btn-logout"),
                tabRegister: document.getElementById("tab-register"),
                tabLogin: document.getElementById("tab-login"),
                registerForm: document.getElementById("register-form"),
                loginForm: document.getElementById("login-form"),
                registerEmail: document.getElementById("register-email"),
                registerPassword: document.getElementById("register-password"),
                registerPasswordRepeat: document.getElementById("register-password-repeat"),
                loginEmail: document.getElementById("login-email"),
                loginPassword: document.getElementById("login-password"),
                createTaskForm: document.getElementById("create-task-form"),
                newTitle: document.getElementById("new-title"),
                newDescription: document.getElementById("new-description"),
                filterUnfinished: document.getElementById("filter-unfinished"),
                searchInput: document.getElementById("search-input"),
                tasksList: document.getElementById("tasks-list"),
                statTotal: document.getElementById("stat-total"),
                statOpen: document.getElementById("stat-open"),
                statDone: document.getElementById("stat-done"),
            };
        }

        init() {
            this.bindEvents();
            this.createTaskModal = this.dom.addTaskModal
                ? bootstrap.Modal.getOrCreateInstance(this.dom.addTaskModal)
                : null;
            this.restoreUiPreferences();
            this.refreshLayoutByAuth();
            this.startFrontendAutoReload();
        }

        bindEvents() {
            this.dom.tabRegister.addEventListener("click", () => this.showAuthForm("register"));
            this.dom.tabLogin.addEventListener("click", () => this.showAuthForm("login"));
            this.dom.registerForm.addEventListener("submit", (event) => this.handleRegister(event));
            this.dom.loginForm.addEventListener("submit", (event) => this.handleLogin(event));
            this.dom.btnLogout.addEventListener("click", () => this.handleLogout());
            this.dom.createTaskForm.addEventListener("submit", (event) => this.handleCreateTask(event));

            this.dom.filterUnfinished.addEventListener("change", () => {
                this.persistUiPreferences();
                this.loadTasks();
            });

            this.dom.searchInput.addEventListener("input", () => {
                this.persistUiPreferences();
                this.renderTasks();
            });

            this.dom.tasksList.addEventListener("click", (event) => {
                const button = event.target.closest("button[data-action]");
                if (!button) {
                    return;
                }

                const action = button.dataset.action;
                const taskId = Number(button.dataset.taskId);

                if (action === "edit") {
                    this.startEditing(taskId);
                }

                if (action === "cancel-edit") {
                    this.cancelEditing();
                }

                if (action === "save-edit") {
                    this.saveEditing(taskId);
                }

                if (action === "finish") {
                    this.handleFinishTask(taskId);
                }

                if (action === "delete") {
                    this.handleDeleteTask(taskId);
                }
            });
        }

        async startFrontendAutoReload() {
            try {
                const payload = await this.api.getWebVersion();
                this.state.latestWebVersion = payload?.version || null;
            } catch {
                return;
            }

            window.setInterval(async () => {
                try {
                    const payload = await this.api.getWebVersion();
                    const nextVersion = payload?.version || null;
                    if (this.state.latestWebVersion && nextVersion && nextVersion !== this.state.latestWebVersion) {
                        window.location.reload();
                    }
                    this.state.latestWebVersion = nextVersion;
                } catch {
                    // ignore transient polling errors
                }
            }, RELOAD_CHECK_INTERVAL_MS);
        }

        notifySuccess(message) {
            this.toast.show({ title: "Succes", message, variant: "success" });
        }

        notifyError(message) {
            this.toast.show({ title: "Eroare", message, variant: "error", delay: 5200 });
        }

        notifyWarning(message) {
            this.toast.show({ title: "Atentie", message, variant: "warning", delay: 4800 });
        }

        restoreUiPreferences() {
            try {
                const raw = window.localStorage.getItem(UI_PREFS_KEY);
                if (!raw) {
                    return;
                }

                const prefs = JSON.parse(raw);
                this.dom.filterUnfinished.checked = Boolean(prefs.filterUnfinished);
                this.dom.searchInput.value = typeof prefs.searchQuery === "string" ? prefs.searchQuery : "";
            } catch {
                // ignore invalid saved preferences
            }
        }

        persistUiPreferences() {
            const prefs = {
                filterUnfinished: this.dom.filterUnfinished.checked,
                searchQuery: this.dom.searchInput.value || "",
            };
            window.localStorage.setItem(UI_PREFS_KEY, JSON.stringify(prefs));
        }

        showAuthForm(mode) {
            const registerActive = mode === "register";
            this.dom.registerForm.classList.toggle("d-none", !registerActive);
            this.dom.loginForm.classList.toggle("d-none", registerActive);

            this.dom.tabRegister.classList.toggle("btn-success", registerActive);
            this.dom.tabRegister.classList.toggle("btn-outline-success", !registerActive);
            this.dom.tabLogin.classList.toggle("btn-success", !registerActive);
            this.dom.tabLogin.classList.toggle("btn-outline-success", registerActive);
        }

        refreshLayoutByAuth() {
            const token = this.authStore.getToken();
            if (!token) {
                this.dom.authSection.classList.remove("d-none");
                this.dom.tasksSection.classList.add("d-none");
                this.dom.userControls.classList.add("d-none");
                this.dom.userControls.classList.remove("d-flex");
                this.showAuthForm("register");
                return;
            }

            this.dom.authSection.classList.add("d-none");
            this.dom.tasksSection.classList.remove("d-none");
            this.dom.userControls.classList.remove("d-none");
            this.dom.userControls.classList.add("d-flex");
            this.dom.userEmail.textContent = this.authStore.getUserEmail() || "utilizator";
            this.loadTasks();
        }

        async handleRegister(event) {
            event.preventDefault();
            const email = this.dom.registerEmail.value.trim();
            const password = this.dom.registerPassword.value;
            const passwordRepeat = this.dom.registerPasswordRepeat.value;

            if (!email || !password || !passwordRepeat) {
                this.notifyWarning("Completeaza toate campurile de inregistrare.");
                return;
            }

            if (password !== passwordRepeat) {
                this.notifyWarning("Parolele nu coincid.");
                return;
            }

            try {
                await this.api.register(email, password);
                this.dom.registerForm.reset();
                this.notifySuccess("Cont creat. Acum te poti autentifica.");
                this.showAuthForm("login");
                this.dom.loginEmail.value = email;
                this.dom.loginPassword.focus();
            } catch (error) {
                this.notifyError(error.message || "Inregistrarea a esuat.");
            }
        }

        async handleLogin(event) {
            event.preventDefault();
            const email = this.dom.loginEmail.value.trim();
            const password = this.dom.loginPassword.value;

            if (!email || !password) {
                this.notifyWarning("Introdu emailul si parola.");
                return;
            }

            try {
                const data = await this.api.login(email, password);
                this.authStore.setToken(data.access_token);
                this.dom.loginForm.reset();
                this.notifySuccess("Autentificare reusita.");
                this.refreshLayoutByAuth();
            } catch (error) {
                this.notifyError(error.message || "Autentificare esuata.");
            }
        }

        handleLogout() {
            this.authStore.clearToken();
            this.state.tasks = [];
            this.state.editingTaskId = null;
            this.updateStats();
            this.renderTasks();
            this.notifySuccess("Ai fost deconectat.");
            this.refreshLayoutByAuth();
        }

        async loadTasks() {
            this.state.loading = true;
            this.renderTasks();

            try {
                const unfinishedOnly = this.dom.filterUnfinished.checked;
                const tasks = await this.api.listTasks(unfinishedOnly);
                this.state.tasks = Array.isArray(tasks) ? tasks : [];
            } catch (error) {
                this.state.tasks = [];

                if (error.status === 401) {
                    this.notifyWarning("Sesiunea a expirat. Autentifica-te din nou.");
                    this.handleLogout();
                    return;
                }

                this.notifyError(error.message || "Nu am putut incarca sarcinile.");
            } finally {
                this.state.loading = false;
                this.updateStats();
                this.renderTasks();
            }
        }

        getVisibleTasks() {
            const query = this.dom.searchInput.value.trim().toLowerCase();
            if (!query) {
                return this.state.tasks;
            }
            return this.state.tasks.filter((item) => item.titlu.toLowerCase().includes(query));
        }

        updateStats() {
            const total = this.state.tasks.length;
            const done = this.state.tasks.filter((item) => item.finalizata).length;
            const open = total - done;
            this.dom.statTotal.textContent = `Total: ${total}`;
            this.dom.statOpen.textContent = `In progres: ${open}`;
            this.dom.statDone.textContent = `Finalizate: ${done}`;
        }

        renderTasks() {
            const container = this.dom.tasksList;

            if (this.state.loading) {
                container.innerHTML = '<div class="empty-view">Se incarca sarcinile...</div>';
                return;
            }

            const tasks = this.getVisibleTasks();
            if (tasks.length === 0) {
                container.innerHTML = '<div class="empty-view">Nu exista sarcini pentru criteriile curente.</div>';
                return;
            }

            container.innerHTML = tasks.map((task) => this.renderTask(task)).join("");
        }

        renderTask(task) {
            const isEditing = this.state.editingTaskId === task.id;
            const safeTitle = this.escapeHtml(task.titlu || "");
            const safeDescription = this.escapeHtml(task.descriere || "");
            const badgeClass = task.finalizata ? "text-bg-secondary" : "text-bg-success";
            const badgeLabel = task.finalizata ? "Finalizata" : "In progres";

            if (isEditing) {
                return `
                    <article class="note-card stagger-item" data-task-id="${task.id}">
                        <div class="d-flex flex-column gap-2">
                            <input type="text" class="form-control" data-edit-field="title" value="${safeTitle}" maxlength="140">
                            <textarea class="form-control" data-edit-field="description" rows="4" maxlength="1000">${safeDescription}</textarea>
                            <div class="d-flex justify-content-end gap-2">
                                <button class="btn btn-success btn-sm" data-action="save-edit" data-task-id="${task.id}" title="Salveaza">
                                    <i class="bi bi-floppy me-1"></i>Salveaza
                                </button>
                                <button class="btn btn-soft btn-sm" data-action="cancel-edit" data-task-id="${task.id}" title="Renunta">
                                    <i class="bi bi-x-lg me-1"></i>Renunta
                                </button>
                            </div>
                        </div>
                    </article>
                `;
            }

            const descriptionHtml = safeDescription
                ? `<p class="note-body">${safeDescription}</p>`
                : `<p class="note-body note-empty"><i class="bi bi-card-text"></i>Fara descriere</p>`;

            const overlay = task.finalizata
                ? ""
                : `
                    <div class="note-actions">
                        <button class="note-action-btn" data-action="edit" data-task-id="${task.id}" title="Editeaza">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="note-action-btn finish" data-action="finish" data-task-id="${task.id}" title="Finalizeaza">
                            <i class="bi bi-check2"></i>
                        </button>
                        <button class="note-action-btn delete" data-action="delete" data-task-id="${task.id}" title="Sterge">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </div>
                `;

            return `
                <article class="note-card stagger-item ${task.finalizata ? "completed" : ""}" data-task-id="${task.id}">
                    <header class="note-header">
                        <h3 class="note-title">${safeTitle}</h3>
                        <span class="badge ${badgeClass} badge-status">${badgeLabel}</span>
                    </header>
                    ${descriptionHtml}
                    ${overlay}
                </article>
            `;
        }

        startEditing(taskId) {
            this.state.editingTaskId = taskId;
            this.renderTasks();
        }

        cancelEditing() {
            this.state.editingTaskId = null;
            this.renderTasks();
        }

        async saveEditing(taskId) {
            const taskEl = this.dom.tasksList.querySelector(`[data-task-id="${taskId}"]`);
            if (!taskEl) {
                return;
            }

            const titleInput = taskEl.querySelector("[data-edit-field='title']");
            const descriptionInput = taskEl.querySelector("[data-edit-field='description']");
            const titlu = (titleInput?.value || "").trim();
            const descriere = (descriptionInput?.value || "").trim();

            if (!titlu) {
                this.notifyWarning("Titlul sarcinii nu poate fi gol.");
                return;
            }

            try {
                await this.api.updateTask(taskId, titlu, descriere);
                this.state.editingTaskId = null;
                this.notifySuccess("Sarcina a fost actualizata.");
                await this.loadTasks();
            } catch (error) {
                this.notifyError(error.message || "Nu am putut actualiza sarcina.");
            }
        }

        async handleCreateTask(event) {
            event.preventDefault();
            const title = this.dom.newTitle.value.trim();
            const description = this.dom.newDescription.value.trim();

            if (!title) {
                this.notifyWarning("Titlul este obligatoriu pentru o sarcina noua.");
                return;
            }

            try {
                await this.api.createTask(title, description);
                this.dom.createTaskForm.reset();
                if (this.createTaskModal) {
                    this.createTaskModal.hide();
                }
                this.notifySuccess("Sarcina a fost adaugata.");
                await this.loadTasks();
            } catch (error) {
                this.notifyError(error.message || "Nu am putut adauga sarcina.");
            }
        }

        async handleFinishTask(taskId) {
            try {
                await this.api.finishTask(taskId);
                this.notifySuccess("Sarcina a fost finalizata.");
                await this.loadTasks();
            } catch (error) {
                this.notifyError(error.message || "Nu am putut finaliza sarcina.");
            }
        }

        async handleDeleteTask(taskId) {
            const confirmed = window.confirm("Esti sigur ca vrei sa stergi aceasta sarcina?");
            if (!confirmed) {
                return;
            }

            try {
                await this.api.deleteTask(taskId);
                this.notifySuccess("Sarcina a fost stearsa.");
                await this.loadTasks();
            } catch (error) {
                this.notifyError(error.message || "Nu am putut sterge sarcina.");
            }
        }

        escapeHtml(text) {
            const div = document.createElement("div");
            div.textContent = String(text || "");
            return div.innerHTML;
        }
    }

    const app = new TaskApp();
    document.addEventListener("DOMContentLoaded", () => app.init());
})();
