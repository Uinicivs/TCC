export type VariableType = 'text' | 'number' | 'bool' | 'list' | 'object'

export interface Variable {
  displayName: string
  type: VariableType
  required: boolean
}