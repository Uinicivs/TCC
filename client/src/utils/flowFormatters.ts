import type { Node as FlowNode } from '@vue-flow/core'

export interface SchemaNode {
  nodeId: string
  nodeName: string
  parentNodeId: string | null
  isFalseCase: boolean | null
  nodeType: 'START' | 'CONDITIONAL' | 'END'
  metadata: {
    inputs?: Array<{
      displayName: string
      type: 'number' | 'text' | 'bool'
      required: boolean
    }>
    expression?: string
    response?: string | number | boolean | null
  }
}

export function mapSchemaToFlow(schemaNodes: SchemaNode[]): FlowNode[] {
  return schemaNodes.map((schemaNode) => {
    const flowNode: FlowNode = {
      id: schemaNode.nodeId,
      type: schemaNode.nodeType.toLowerCase(),
      position: { x: 0, y: 0 },
      data: {
        title: schemaNode.nodeName,
        parent: schemaNode.parentNodeId,
        children: [],
        isFalseCase: schemaNode.isFalseCase,
        settings: {}
      }
    }

    switch (schemaNode.nodeType) {
      case 'START':
        flowNode.data.settings = {
          inputs: schemaNode.metadata.inputs || []
        }
        break
      case 'CONDITIONAL':
        flowNode.data.settings = {
          expression: schemaNode.metadata.expression || ''
        }
        break
      case 'END':
        flowNode.data.settings = {
          response: schemaNode.metadata.response
        }
        break
    }

    return flowNode
  })
}

export function mapFlowToSchema(flowNodes: FlowNode[]): SchemaNode[] {
  return flowNodes.map((flowNode) => {
    const schemaNode: SchemaNode = {
      nodeId: flowNode.id,
      nodeName: flowNode.data.title,
      parentNodeId: flowNode.data.parent,
      isFalseCase: flowNode.data.isFalseCase || null,
      nodeType: flowNode.type?.toUpperCase() as 'START' | 'CONDITIONAL' | 'END',
      metadata: {}
    }

    switch (flowNode.type) {
      case 'start':
        schemaNode.metadata = {
          inputs: flowNode.data.settings?.inputs || []
        }
        break
      case 'conditional':
        schemaNode.metadata = {
          expression: flowNode.data.settings?.expression || ''
        }
        break
      case 'end':
        schemaNode.metadata = {
          response: flowNode.data.settings?.response || null
        }
        break
    }

    return schemaNode
  })
}
