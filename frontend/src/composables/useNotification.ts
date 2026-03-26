import { ref, readonly } from 'vue'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: number
  type: NotificationType
  message: string
  timeout: number
}

const notifications = ref<Notification[]>([])
let nextId = 0

function addNotification(
  type: NotificationType,
  message: string,
  timeout = 5000
): void {
  const id = nextId++
  notifications.value.push({ id, type, message, timeout })

  if (timeout > 0) {
    setTimeout(() => {
      remove(id)
    }, timeout)
  }
}

function remove(id: number): void {
  const index = notifications.value.findIndex((n) => n.id === id)
  if (index !== -1) {
    notifications.value.splice(index, 1)
  }
}

function success(message: string, timeout?: number): void {
  addNotification('success', message, timeout)
}

function error(message: string, timeout?: number): void {
  addNotification('error', message, timeout ?? 8000)
}

function warning(message: string, timeout?: number): void {
  addNotification('warning', message, timeout)
}

function info(message: string, timeout?: number): void {
  addNotification('info', message, timeout)
}

export function useNotification() {
  return {
    notifications: readonly(notifications),
    success,
    error,
    warning,
    info,
    remove,
  }
}
