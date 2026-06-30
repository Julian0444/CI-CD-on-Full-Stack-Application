import React, { useState } from "react";

export default function TodoForm({ onAdd, disabled = false }) {
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmed = title.trim();

    if (!trimmed) {
      setError("El título es requerido");
      return;
    }

    setError("");
    if (onAdd) {
      await onAdd(trimmed);
    }
    setTitle("");
  };

  return (
    <form onSubmit={handleSubmit} className="todo-form">
      <div className="todo-form__row">
        <input
          type="text"
          className="todo-form__input"
          placeholder="¿Qué necesitás hacer?"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          aria-label="Título de la tarea"
          disabled={disabled}
          data-cy="todo-input"
        />
        <button type="submit" className="btn btn--primary" disabled={disabled} data-cy="add-btn">
          Agregar tarea
        </button>
      </div>
      {error && (
        <span role="alert" className="form-error">
          {error}
        </span>
      )}
    </form>
  );
}
