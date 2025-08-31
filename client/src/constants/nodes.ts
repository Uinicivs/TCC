import ConditionalNodeConfig from '@/components/flows/show/ConditionalNodeConfig.vue'

import type { IMappedNodes } from '@/interfaces/node'

export const nodes: Record<string, IMappedNodes> = {
  start: {
    name: 'Início',
    type: 'start',
    icon: 'pi-circle',
    extraClasses: 'text-emerald-500',
  },

  conditional: {
    name: 'Condicional',
    description: 'Define o próximo caminho conforme a regra avaliada.',
    type: 'conditional',
    icon: 'pi-stop',
    extraClasses: 'text-amber-500 rotate-45',
    configComponent: ConditionalNodeConfig,
  },
  end: {
    name: 'Fim',
    description: 'Finaliza o fluxo neste ponto.',
    type: 'end',
    icon: 'pi-circle',
    extraClasses: 'text-red-500',
  },
}
