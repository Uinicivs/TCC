import ConditionalNodeConfig from '@/components/home/ConditionalNodeConfig.vue'

import type { IMappedNodes } from '@/interfaces/node'

export const nodes: Record<string, IMappedNodes> = {
  trigger: {
    name: 'Trigger',
    type: 'trigger',
    icon: 'pi-bolt',
    iconColor: 'text-emerald-500',
  },

  conditional: {
    name: 'Conditional',
    type: 'conditional',
    icon: 'pi-question-circle',
    iconColor: 'text-amber-500',
    configComponent: ConditionalNodeConfig,
  },
}
