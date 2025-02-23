export interface Task {
  id: number
  title: string
  description?: string
  priority: 'High' | 'Medium' | 'Low'
  status: 'Pending' | 'In Progress' | 'Completed'
  deadline?: string
  labels?: string[]
} 