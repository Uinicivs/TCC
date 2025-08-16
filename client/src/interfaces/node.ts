import type { Component } from 'vue'

type INodeTypes = 'trigger' | 'conditional'

export interface INode {
  title: string
  description?: string
  settings?: Record<string, unknown>
}

export interface IMappedNodes {
  name: Capitalize<INodeTypes>
  type: INodeTypes
  icon: string
  iconColor: string
  configComponent?: Component
}
