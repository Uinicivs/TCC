export type VariableType = 'text' | 'number' | 'bool' | 'list'

export interface Variable {
  displayName: string
  type: VariableType
  required: boolean
}
