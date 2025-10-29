import api from './api'
import type { IFlow } from '@/interfaces/flow'
import type { SchemaNode } from '@/utils/flowFormatters'
import { AxiosError } from 'axios'
import type { TestFlowResult } from '@/interfaces/testFlow'

export type TCreateFlowPayload = Pick<IFlow, 'flowName' | 'flowDescription'>

export const createFlow = async (payload: TCreateFlowPayload): Promise<IFlow> => {
  try {
    const response = await api.post<IFlow>('/decision_flows', payload)

    return {
      ...response.data,
      createdAt: new Date(response.data.createdAt),
      updatedAt: new Date(response.data.updatedAt),
    }
  } catch {
    throw new Error('Falha ao criar o fluxo. Tente novamente.')
  }
}

export const getFlows = async (): Promise<IFlow[]> => {
  try {
    const response = await api.get<IFlow[]>('/decision_flows')

    return response.data.map((flow) => ({
      ...flow,
      createdAt: new Date(flow.createdAt),
      updatedAt: new Date(flow.updatedAt),
    }))
  } catch {
    throw new Error('Falha ao buscar os fluxos. Tente novamente.')
  }
}

export const getFlowById = async (id: string): Promise<IFlow> => {
  try {
    const response = await api.get<IFlow>(`/decision_flows/${id}`)

    return {
      ...response.data,
      createdAt: new Date(response.data.createdAt),
      updatedAt: new Date(response.data.updatedAt),
    }
  } catch (error) {
    if (error instanceof AxiosError) {
      if (error.response?.status === 404) {
        throw new Error('Fluxo de decisão não encontrado.')
      }
      if (error.response?.status === 401 || error.response?.status === 403) {
        throw new Error('Você não tem permissão para acessar este fluxo.')
      }
    }
    throw new Error('Ops! Ocorreu um erro ao buscar o fluxo. Tente novamente.')
  }
}

export const updateFlow = async (id: string, payload: Partial<TCreateFlowPayload>) => {
  try {
    await api.patch<IFlow>(`/decision_flows/${id}`, payload)
  } catch {
    throw new Error('Falha ao atualizar o fluxo. Tente novamente.')
  }
}

export const deleteFlow = async (id: string): Promise<void> => {
  try {
    await api.delete(`/decision_flows/${id}`)
  } catch {
    throw new Error('Falha ao deletar o fluxo. Tente novamente.')
  }
}

export const updateFlowNodes = async (id: string, nodes: SchemaNode[]): Promise<void> => {
  try {
    await api.put(`/decision_flows/${id}/nodes`, nodes)
  } catch {
    throw new Error('Falha ao atualizar os nós do fluxo. Tente novamente.')
  }
}

export const evaluateFlow = async (
  id: string,
  variables: Record<string, unknown>,
): Promise<unknown> => {
  try {
    const response = await api.post(`/decision_flows/${id}/evaluate`, variables)
    return response.data
  } catch {
    throw new Error('Falha ao executar o fluxo. Tente novamente.')
  }
}

export const testFlow = async (id: string): Promise<TestFlowResult> => {
  try {
    const response = await api.get(`/decision_flows/${id}/test`)
    return response.data as TestFlowResult
  } catch {
    throw new Error('Falha ao testar o fluxo. Tente novamente.')
  }
}
