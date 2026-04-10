import request from './request'

export interface DeviceListParams {
  page?: number
  size?: number
  search?: string
}

export interface Device {
  id: string
  name: string
  model: string
  status: string
  lastOnline: string
  petId?: number
  petName?: string
}

export const deviceApi = {
  getList: (params: DeviceListParams) =>
    request.get<any, { data: { items: Device[]; total: number } }>('/devices', {
      params,
    }),

  getDetail: (id: string) =>
    request.get<any, { data: Device }>(`/devices/${id}`),

  create: (data: Partial<Device>) =>
    request.post<any, { data: Device }>('/devices', data),

  update: (id: string, data: Partial<Device>) =>
    request.put<any, { data: Device }>(`/devices/${id}`, data),

  delete: (id: string) => request.delete(`/devices/${id}`),

  heartbeat: (id: string) =>
    request.post(`/devices/${id}/heartbeat`),
}
