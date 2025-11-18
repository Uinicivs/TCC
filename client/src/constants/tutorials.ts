import type { IStep } from '@/interfaces/tutorial'

import createFlow from '@/assets/gifs/createFlow.gif'
import rightClickMenu from '@/assets/gifs/rightClickMenu.gif'
import toggleMode from '@/assets/gifs/toggleMode.gif'
import createNodeFlow from '@/assets/gifs/createNodeFlow.gif'
import testFlow from '@/assets/gifs/testFlow.gif'
import executeFlow from '@/assets/gifs/executeFlow.gif'

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

export const flowEditorTutorial: IStep[] = [
  {
    targetId: 'flow-editor-canvas',
    title: 'Bem-vindo ao Editor de Fluxos! 🛠️',
    description: [
      'Este é o coração do Rulify! Aqui você cria e visualiza seus fluxos de decisão de forma visual e intuitiva.',
      'Vamos explorar todas as funcionalidades disponíveis.',
    ],
    align: 'center',
  },
  {
    targetId: 'back-button',
    title: 'Voltando para Home 🏠',
    description:
      'Use este botão para voltar à tela inicial. Não se preocupe, todas as suas alterações são salvas automaticamente!',
    align: 'start',
    side: 'bottom',
  },
  {
    targetId: 'body',
    title: 'Criando seu Primeiro Nó',
    imagePath: createNodeFlow,
    description: [
      'Todo fluxo começa com um nó inicial. Clique neste botão para adicionar o primeiro nó do seu fluxo.',
      'Você poderá escolher entre diferentes tipos: Início, Condicional ou Fim.',
    ],
    align: 'center',
  },
  {
    targetId: 'flow-background',
    title: 'Fluxo 🎨',
    description: [
      'Esta é a área de trabalho onde seus nós e conexões aparecem.',
      'Você pode arrastar os nós para organizá-los da maneira que preferir. O layout é totalmente personalizável!',
    ],
    align: 'center',
  },
  {
    targetId: 'flow-controls',
    title: 'Controles de Visualização 🔍',
    description: [
      'Use estes controles para navegar pelo fluxo:',
      '• Zoom In/Out: Aproximar ou afastar a visualização',
      '• Fit View: Ajustar o zoom para ver todo o fluxo',
    ],
    align: 'end',
    side: 'left',
  },
  {
    targetId: 'test-flow-button',
    title: 'Testando seu Fluxo ✨',
    imagePath: testFlow,
    description: [
      'Antes de executar em produção, teste seu fluxo! Clique aqui para simular diferentes cenários.',
      'Você poderá ver quais caminhos são alcançáveis e identificar possíveis problemas na lógica.',
    ],
    align: 'end',
    side: 'top',
  },
  {
    targetId: 'execute-flow-button',
    title: 'Executando o Fluxo 🚀',
    imagePath: executeFlow,
    description: [
      'Quando seu fluxo estiver pronto, clique aqui para executá-lo!',
      'Você fornecerá os valores de entrada e receberá o resultado baseado na lógica que você criou.',
    ],
    align: 'end',
    side: 'top',
  },
  {
    targetId: 'body',
    title: 'Dicas Importantes! 💡',
    description: [
      '• Nós de Início: Definem as variáveis de entrada do fluxo',
      '• Nós Condicionais: Criam ramificações baseadas em regras expressões lógicas',
      '• Nós de Fim: Definem os resultados finais do fluxo',
      'Clique com botão direito nos nós para editar, duplicar ou excluir',
      'As alterações são salvas automaticamente',
    ],
    align: 'center',
  },
  {
    targetId: 'flow-editor-canvas',
    title: 'Quer Ver na Prática? 🎬',
    description: [
      'Preparamos um vídeo completo mostrando passo a passo como criar, configurar, testar e executar um fluxo de decisão.',
    ],
    align: 'center',
    link: {
      url: 'https://youtu.be/STzLSFdqOPY',
      label: 'Assistir Tutorial no YouTube',
    },
  },
  {
    targetId: 'flow-editor-canvas',
    title: 'Pronto para Começar! 🎯',
    description:
      'Agora você conhece todas as ferramentas para criar fluxos incríveis. Comece adicionando seu primeiro nó e construa a lógica do seu negócio de forma visual!',
    align: 'center',
  },
]
