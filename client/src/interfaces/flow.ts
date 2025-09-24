import type { SchemaNode } from '@/utils/flowFormatters'

export interface IFlow {
  flowId: string
  flowName: string
  flowDescription?: string
  nodes?: SchemaNode[]
  createdAt: Date
  updatedAt: Date
}
