import type { Component } from 'vue'

type INodeTypes = 'trigger' | 'conditional'

export interface INode {
  title: string
  description?: string
  config?: Record<string, any>
}

export interface IMappedNodes {
  name: Capitalize<INodeTypes>
  type: INodeTypes
  icon: string
  iconColor: string
  configComponent?: Component
}
