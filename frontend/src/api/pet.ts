import request from './request'

export interface Pet {
  id: number
  name: string
  species: string
  level: number
  emotion: string
  hunger: number
  happiness: number
  deviceId: string
  deviceName?: string
}

export interface InteractionParams {
  type: string
  content: string
}

export const petApi = {
  getList: (params: { page?: number; size?: number }) =>
    request.get<any, { data: { items: Pet[]; total: number } }>('/pets', {
      params,
    }),

  getDetail: (id: number) =>
    request.get<any, { data: Pet }>(`/pets/${id}`),

  create: (data: Partial<Pet>) =>
    request.post<any, { data: Pet }>('/pets', data),

  update: (id: number, data: Partial<Pet>) =>
    request.put<any, { data: Pet }>(`/pets/${id}`, data),

  delete: (id: number) => request.delete(`/pets/${id}`),

  interact: (id: number, params: InteractionParams) =>
    request.post<any, { data: any }>(`/pets/${id}/interact`, params),

  getHistory: (id: number, params: { page?: number; size?: number }) =>
    request.get<any, { data: any }>(`/pets/${id}/history`, { params }),
}
