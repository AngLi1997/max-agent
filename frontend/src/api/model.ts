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

export interface ModelListResult {
  list: ProviderItem[]
  total: number
}

/* ---- Provider APIs ---- */

export function getProviderListApi(params?: { name?: string; type?: string }): Promise<ModelListResult> {
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

export function getChatStreamUrl(modelId: number): string {
  return `/api/providers/models/${modelId}/chat`
}
