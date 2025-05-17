import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002/api/v1'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor for auth
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            const response = await this.api.post('/auth/refresh', {
              refresh_token: refreshToken,
            })

            const { access_token } = response.data
            localStorage.setItem('access_token', access_token)

            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return this.api(originalRequest)
          } catch (refreshError) {
            // Refresh failed, redirect to login
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.api.post('/auth/login', { email, password })
    return response.data
  }

  async register(data: RegisterData) {
    const response = await this.api.post('/auth/register', data)
    return response.data
  }

  async logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // Users endpoints
  async getUsers() {
    const response = await this.api.get('/users')
    return response.data
  }

  async getUser(id: number) {
    const response = await this.api.get(`/users/${id}`)
    return response.data
  }

  async updateUser(id: number, data: UpdateUserData) {
    const response = await this.api.put(`/users/${id}`, data)
    return response.data
  }

  async deleteUser(id: number) {
    const response = await this.api.delete(`/users/${id}`)
    return response.data
  }

  // Projects endpoints
  async getProjects() {
    const response = await this.api.get('/projects')
    return response.data
  }

  async getProject(id: number) {
    const response = await this.api.get(`/projects/${id}`)
    return response.data
  }

  async createProject(data: CreateProjectData) {
    const response = await this.api.post('/projects', data)
    return response.data
  }

  async updateProject(id: number, data: UpdateProjectData) {
    const response = await this.api.put(`/projects/${id}`, data)
    return response.data
  }

  async deleteProject(id: number) {
    const response = await this.api.delete(`/projects/${id}`)
    return response.data
  }

  // Experiments endpoints
  async getExperiments() {
    const response = await this.api.get('/experiments')
    return response.data
  }

  async getExperiment(id: number) {
    const response = await this.api.get(`/experiments/${id}`)
    return response.data
  }

  async createExperiment(data: CreateExperimentData) {
    const response = await this.api.post('/experiments', data)
    return response.data
  }

  async updateExperiment(id: number, data: UpdateExperimentData) {
    const response = await this.api.put(`/experiments/${id}`, data)
    return response.data
  }

  async deleteExperiment(id: number) {
    const response = await this.api.delete(`/experiments/${id}`)
    return response.data
  }

  // Documents endpoints
  async getDocuments() {
    const response = await this.api.get('/documents')
    return response.data
  }

  async getDocument(id: number) {
    const response = await this.api.get(`/documents/${id}`)
    return response.data
  }

  async uploadDocument(file: File, metadata: DocumentMetadata) {
    const formData = new FormData()
    formData.append('file', file)
    Object.entries(metadata).forEach(([key, value]) => {
      formData.append(key, value.toString())
    })

    const response = await this.api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async uploadDocumentVersion(documentId: number, file: File, versionComment?: string) {
    const formData = new FormData()
    formData.append('file', file)
    if (versionComment) {
      formData.append('version_comment', versionComment)
    }

    const response = await this.api.post(`/documents/${documentId}/versions`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async getDocumentVersions(documentId: number) {
    const response = await this.api.get(`/documents/${documentId}/versions`)
    return response.data
  }

  async deleteDocument(id: number) {
    const response = await this.api.delete(`/documents/${id}`)
    return response.data
  }

  // Knowledge Graph endpoints
  async createNode(data: CreateNodeData) {
    const response = await this.api.post('/knowledge_graph/nodes', data)
    return response.data
  }

  async getNode(nodeId: string) {
    const response = await this.api.get(`/knowledge_graph/nodes/${nodeId}`)
    return response.data
  }

  async createRelationship(data: CreateRelationshipData) {
    const response = await this.api.post('/knowledge_graph/relationships', data)
    return response.data
  }

  async searchKnowledgeGraph(searchQuery: SearchQuery) {
    const response = await this.api.post('/knowledge_graph/search', searchQuery)
    return response.data
  }

  async findPath(startId: string, endId: string, maxDepth?: number) {
    const response = await this.api.get('/knowledge_graph/paths', {
      params: { start_id: startId, end_id: endId, max_depth: maxDepth },
    })
    return response.data
  }
}

export const apiService = new ApiService()

// Type definitions
export interface RegisterData {
  email: string
  password: string
  full_name: string
}

export interface UpdateUserData {
  email?: string
  full_name?: string
  is_active?: boolean
}

export interface CreateProjectData {
  title: string
  description?: string
  status?: string
}

export interface UpdateProjectData {
  title?: string
  description?: string
  status?: string
}

export interface CreateExperimentData {
  title: string
  project_id: number
  description?: string
  status?: string
  start_date?: string
  end_date?: string
}

export interface UpdateExperimentData {
  title?: string
  description?: string
  status?: string
  start_date?: string
  end_date?: string
}

export interface DocumentMetadata {
  title: string
  description?: string
  project_id?: number
  experiment_id?: number
  tags?: string
}

export interface CreateNodeData {
  node_type: string
  node_id: string
  properties: Record<string, any>
}

export interface CreateRelationshipData {
  source_id: string
  target_id: string
  relationship_type: string
  properties?: Record<string, any>
}

export interface SearchQuery {
  query?: string
  node_types?: string[]
  limit?: number
  properties?: Record<string, any>
}