import type { IStep } from '@/interfaces/tutorial'

import createFlow from '@/assets/gifs/createFlow.gif'
import rightClickMenu from '@/assets/gifs/rightClickMenu.gif'
import toggleMode from '@/assets/gifs/toggleMode.gif'

export const homeTutorial: IStep[] = [
  {
    targetId: 'body',
    title: 'Bem-vindo ao Rulify! 🎉',
    align: 'center',
    description: [
      'Aqui está a sua central de controle! Nesta tela você gerencia todos os seus fluxos de decisão.',
      'Vamos fazer um tour rápido para você aproveitar ao máximo a plataforma.',
    ],
  },
  {
    targetId: 'create-flow-button',
    title: 'Criando Novos Fluxos ✨',
    imagePath: createFlow,
    description: [
      'Clique neste botão para criar um novo fluxo de decisão. Você pode criar até 10 fluxos diferentes.',
      'Cada fluxo pode representar uma regra de negócio, processo ou lógica de decisão automatizada.',
    ],
    align: 'start',
    side: 'top',
  },
  {
    targetId: 'view-mode-toggle',
    title: 'Modos de Visualização 👀',
    imagePath: toggleMode,
    description:
      'Prefere ver seus fluxos em cards ou em tabela? Use este seletor para alternar entre os modos de exibição. A sua preferência será salva automaticamente!',
    align: 'start',
    side: 'right',
  },
  {
    targetId: 'body',
    title: 'Seus Fluxos 📋',
    description:
      'Aqui ficam listados todos os seus fluxos criados. Você pode visualizar informações como nome, descrição e data da última atualização de cada fluxo.',
    align: 'center',
  },
  {
    targetId: 'flow-cards-grid',
    title: 'Acessando um Fluxo 🖱️',
    description:
      'Clique em qualquer card para abrir e visualizar o fluxo completo. Você será redirecionado para o editor visual onde poderá ver e editar todos os nós e conexões.',
    align: 'center',
    side: 'top',
  },
  {
    targetId: 'flow-cards-grid',
    title: 'Dica Super Importante! ⚡',
    imagePath: rightClickMenu,
    description: [
      'Clique com o botão direito do mouse em qualquer fluxo para abrir um menu especial',
      'Este é o jeito mais rápido de gerenciar seus fluxos!',
    ],
    align: 'start',
    side: 'over',
  },
  {
    targetId: 'help-button',
    title: 'Estou sempre aqui! 💡',
    description:
      'Se precisar rever este tutorial a qualquer momento, basta clicar no botão de ajuda (?) no canto superior direito. Agora você está pronto para criar fluxos incríveis!',
    align: 'end',
    side: 'bottom',
  },
]
