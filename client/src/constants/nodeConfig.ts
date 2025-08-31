export const EXCLUDED_NODE_TYPES: string[] = ['start']

export const DEFAULT_NODE_TITLES: Record<string, string> = {
  start: 'Início',
  end: 'Fim',
}

export const getDefaultNodeTitle = (nodeType: string): string => {
  return DEFAULT_NODE_TITLES[nodeType] || ''
}
