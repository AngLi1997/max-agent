// frontend/src/api/model.ts
import request from './request'

/* ---- Types ---- */

export interface LlmModelItem {
  id: number
  model_name: string
  status: string
  created_at: string
}

export interface ProviderItem {
  id: number
  name: string
  type: string
  api_url: string
  api_key: string | null
  status: string
  models: LlmModelItem[]
  created_at: string
  updated_at: string
}

export interface ProviderCreateParams {
  name: string
  type: string
  api_url: string
  api_key?: string
  models: string[]
}

export interface ProviderUpdateParams {
  name?: string
  api_url?: string
  api_key?: string
  status?: string
}

export interface FetchModelsParams {
  type: string
  api_url: string
  api_key?: string
}

// Flat model list item (from GET /api/providers/models)
export interface ModelListItem {
  id: number
  provider_id: number
  model_name: string
  provider_name: string
  provider_type: string
  provider_api_url: string
  status: string
  created_at: string
}

export interface ModelUpdateParams {
  status?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequestParams {
  messages: ChatMessage[]
}

export interface ProviderListResult {
  list: ProviderItem[]
  total: number
}

export interface ModelListResult {
  list: ModelListItem[]
  total: number
}

/* ---- Provider APIs ---- */

export function getProviderListApi(params?: { name?: string; type?: string }): Promise<ProviderListResult> {
  return request.get('/providers/', { params })
}

export function getProviderApi(id: number): Promise<ProviderItem> {
  return request.get(`/providers/${id}`)
}

export function createProviderApi(data: ProviderCreateParams): Promise<ProviderItem> {
  return request.post('/providers/', data)
}

export function updateProviderApi(id: number, data: ProviderUpdateParams): Promise<ProviderItem> {
  return request.put(`/providers/${id}`, data)
}

export function deleteProviderApi(id: number): Promise<void> {
  return request.delete(`/providers/${id}`)
}

export function fetchRemoteModelsApi(data: FetchModelsParams): Promise<{ models: string[] }> {
  return request.post('/providers/fetch-models', data)
}

export function deleteModelApi(modelId: number): Promise<void> {
  return request.delete(`/providers/models/${modelId}`)
}

/* ---- Flat Model APIs ---- */

export function getModelListApi(params?: { name?: string; type?: string }): Promise<ModelListResult> {
  return request.get('/providers/models', { params })
}

export function updateModelApi(id: number, data: ModelUpdateParams): Promise<void> {
  return request.put(`/providers/models/${id}`, data)
}

/** Returns the SSE chat endpoint URL for direct fetch usage */
export function getChatStreamUrl(modelId: number): string {
  return `/api/providers/models/${modelId}/chat`
}
