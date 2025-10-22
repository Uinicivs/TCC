import type { Node as FlowNode } from '@vue-flow/core'

export interface SchemaNode {
  nodeId: string
  nodeName: string
  parentNodeId: string | null
  isFalseCase: boolean
  nodeType: 'START' | 'CONDITIONAL' | 'END'
  nodePositionX: number
  nodePositionY: number
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
      position: {
        x: schemaNode.nodePositionX,
        y: schemaNode.nodePositionY,
      },
      data: {
        title: schemaNode.nodeName,
        parent: schemaNode.parentNodeId,
        children: [],
        isFalseCase: schemaNode.isFalseCase,
        settings: {},
      },
    }

    switch (schemaNode.nodeType) {
      case 'START':
        flowNode.data.settings = {
          inputs: schemaNode.metadata.inputs || [],
        }
        break
      case 'CONDITIONAL':
        flowNode.data.settings = {
          expression: schemaNode.metadata.expression || '',
        }
        break
      case 'END':
        flowNode.data.settings = {
          response: schemaNode.metadata.response,
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
      nodePositionX: flowNode.position.x,
      nodePositionY: flowNode.position.y,
      isFalseCase: flowNode.data.isFalseCase || false,
      nodeType: flowNode.type?.toUpperCase() as 'START' | 'CONDITIONAL' | 'END',
      metadata: {},
    }

    switch (flowNode.type) {
      case 'start':
        schemaNode.metadata = {
          inputs: flowNode.data.settings?.inputs || [],
        }
        break
      case 'conditional':
        schemaNode.isFalseCase = flowNode.data.isFalseCase || false
        schemaNode.metadata = {
          expression: flowNode.data.settings?.expression || '',
        }
        break
      case 'end':
        schemaNode.metadata = {
          response: flowNode.data.settings?.response || false,
        }
        break
    }

    return schemaNode
  })
}
