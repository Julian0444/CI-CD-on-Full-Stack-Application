import React from "react";
import TodoItem from "./TodoItem";

export default function TodoList({ todos, onToggle, onDelete, onUpdate }) {
  if (todos.length === 0) {
    return (
      <div className="empty">
        <span className="empty__icon" aria-hidden="true">📝</span>
        <p role="status" className="empty__text">
          No hay tareas cargadas.
        </p>
        <span className="empty__hint">Agregá tu primera tarea para empezar.</span>
      </div>
    );
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
          onUpdate={onUpdate}
        />
      ))}
    </ul>
  );
}
