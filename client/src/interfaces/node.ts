import type { Component } from 'vue'

type INodeTypes = 'start' | 'conditional' | 'end'

export interface INode {
  title: string
  description?: string
  settings?: Record<string, unknown>
  parent: string | null
  children?: Array<string>
  isFalseCase?: boolean
}

export interface IMappedNodes {
  name: string
  type: INodeTypes
  description?: string
  icon: string
  extraClasses: string
  configComponent?: Component
}
