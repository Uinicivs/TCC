export interface TestFlowReduction {
  nodeId: string
  original: string
  simplified: string
  removedParts?: string[]
}

export interface TestFlowPruned {
  nodeId: string
  isFalseCase?: boolean
  reason?: string
}

export interface TestFlowUncovered {
  nodeId: string
  constraints?: string[]
}

export interface TestFlowCase {
  endNodeId: string
  endMetadata?: Record<string, unknown>
  constraints?: string[]
  concrete?: Record<string, unknown>
}

export interface TestFlowCoverage {
  endCount: number
  totalEndNodes: number
}

export interface TestFlowResult {
  cases?: TestFlowCase[]
  pruned?: TestFlowPruned[]
  reductions?: TestFlowReduction[]
  uncovered?: TestFlowUncovered[]
  coverage?: TestFlowCoverage
}
