export const EXCLUDED_NODE_TYPES: string[] = ['start']

export const DEFAULT_NODE_TITLES: Record<string, string> = {
  start: 'Start',
  end: 'End',
}

export const getDefaultNodeTitle = (nodeType: string): string => {
  return DEFAULT_NODE_TITLES[nodeType] || ''
}

export const getAvailableNodeTypes = (excludedTypes: string[] = []): string[] => {
  const allExcludedTypes = [...EXCLUDED_NODE_TYPES, ...excludedTypes]
  return allExcludedTypes
}
