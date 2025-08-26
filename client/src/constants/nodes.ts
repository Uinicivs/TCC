import ConditionalNodeConfig from '@/components/home/ConditionalNodeConfig.vue'

import type { IMappedNodes } from '@/interfaces/node'

export const nodes: Record<string, IMappedNodes> = {
  start: {
    name: 'Start',
    type: 'start',
    icon: 'pi-bolt',
    iconColor: 'text-emerald-500',
  },

  conditional: {
    name: 'Conditional',
    description: 'Lorem ipsum',
    type: 'conditional',
    icon: 'pi-question-circle',
    iconColor: 'text-amber-500',
    configComponent: ConditionalNodeConfig,
  },
  end: {
    name: 'End',
    description: 'Lorem ipsum',
    type: 'end',
    icon: 'pi-flag',
    iconColor: 'text-red-500',
  },
}
