import React, { useCallback, useEffect, useState } from "react";
import "./App.css";
import RegisterForm from "./components/RegisterForm";
import TodoForm from "./components/TodoForm";
import TodoList from "./components/TodoList";
import Toast from "./components/Toast";
import {
  registerUser,
  loginUser,
  getTodos,
  createTodo,
  updateTodo,
  deleteTodo,
} from "./services/api";

const emptyToast = { message: "", type: "info" };

function App() {
  const [currentUser, setCurrentUser] = useState("");
  const [todos, setTodos] = useState([]);
  const [isLoadingTodos, setIsLoadingTodos] = useState(false);
  const [toast, setToast] = useState(emptyToast);

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type });
  }, []);

  const clearToast = useCallback(() => {
    setToast(emptyToast);
  }, []);

  const loadTodos = useCallback(
    async (email) => {
      if (!email) {
        setTodos([]);
        return;
      }
      setIsLoadingTodos(true);
      try {
        const response = await getTodos(email);
        setTodos(response.todos ?? []);
      } catch (error) {
        showToast(error.message, "error");
      } finally {
        setIsLoadingTodos(false);
      }
    },
    [showToast]
  );

  useEffect(() => {
    loadTodos(currentUser);
  }, [currentUser, loadTodos]);

  const handleAuthSuccess = useCallback(
    (email, message) => {
      setCurrentUser(email);
      showToast(message ?? "Sesión iniciada", "success");
    },
    [showToast]
  );

  const handleRegister = async ({ email, password }) => {
    try {
      const response = await registerUser({ email, password });
      handleAuthSuccess(email, response.message ?? "Usuario registrado correctamente");
    } catch (error) {
      showToast(error.message, "error");
    }
  };

  const handleLogin = async ({ email, password }) => {
    try {
      const response = await loginUser({ email, password });
      handleAuthSuccess(email, response.message ?? "Inicio de sesión exitoso");
    } catch (error) {
      showToast(error.message, "error");
    }
  };

  const handleLogout = () => {
    setCurrentUser("");
    setTodos([]);
    showToast("Sesión cerrada", "info");
  };

  const handleCreateTodo = async (title) => {
    if (!currentUser) {
      showToast("Debes iniciar sesión para crear tareas", "warning");
      return;
    }

    try {
      const response = await createTodo({ email: currentUser, title });
      const created = response.todo ?? response;
      setTodos((prev) => [...prev, created]);
      showToast("Tarea creada", "success");
    } catch (error) {
      showToast(error.message, "error");
    }
  };

  const handleToggleTodo = async (id, completed) => {
    try {
      const response = await updateTodo(id, { completed: !completed });
      const updated = response.todo ?? response;
      setTodos((prev) => prev.map((todo) => (todo.id === id ? updated : todo)));
    } catch (error) {
      showToast(error.message, "error");
    }
  };

  const handleRenameTodo = async (id, title) => {
    const trimmed = title.trim();
    if (!trimmed) {
      showToast("El título es requerido", "warning");
      return;
    }

    try {
      const response = await updateTodo(id, { title: trimmed });
      const updated = response.todo ?? response;
      setTodos((prev) => prev.map((todo) => (todo.id === id ? updated : todo)));
      showToast("Tarea actualizada", "success");
    } catch (error) {
      showToast(error.message, "error");
    }
  };

  const handleDeleteTodo = async (id) => {
    try {
      await deleteTodo(id);
      setTodos((prev) => prev.filter((todo) => todo.id !== id));
      showToast("Tarea eliminada", "info");
    } catch (error) {
      showToast(error.message, "error");
    }
  };

  const pendingCount = todos.filter((todo) => !todo.completed).length;

  return (
    <div className="app">
      <header className="brand">
        <span className="brand__mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </span>
        <h1>To-Do List</h1>
        <p className="brand__tagline">
          Una app full-stack desplegada con un pipeline CI/CD completo.
        </p>
      </header>

      <main className={currentUser ? "shell shell--wide" : "shell"}>
        {currentUser ? (
          <section aria-labelledby="todos-section-title" className="panel todo-panel">
            <div className="todo-panel__header">
              <div>
                <h2 id="todos-section-title" className="section__title">
                  Mis tareas
                </h2>
                <p className="section__subtitle">
                  Sesión activa como <strong>{currentUser}</strong>
                </p>
              </div>

              <div className="todo-panel__meta">
                <span className="badge">
                  {pendingCount} pendiente{pendingCount === 1 ? "" : "s"}
                </span>
                <button type="button" className="btn btn--outline" onClick={handleLogout}>
                  Cerrar sesión
                </button>
              </div>
            </div>

            <TodoForm onAdd={handleCreateTodo} disabled={isLoadingTodos} />

            {isLoadingTodos ? (
              <p role="status" className="hint">
                Cargando tareas...
              </p>
            ) : (
              <TodoList
                todos={todos}
                onToggle={handleToggleTodo}
                onDelete={handleDeleteTodo}
                onUpdate={handleRenameTodo}
              />
            )}
          </section>
        ) : (
          <RegisterForm
            onRegister={handleRegister}
            onLogin={handleLogin}
            disabled={Boolean(currentUser)}
            defaultEmail={currentUser}
          />
        )}
      </main>

      <footer className="footer">
        <span>React · Django REST · PostgreSQL</span>
        <span className="footer__dot">•</span>
        <span>GitHub Actions · SonarCloud · Docker · Render</span>
      </footer>

      <Toast message={toast.message} type={toast.type} onClose={clearToast} />
    </div>
  );
}

export default App;
