import 'driver.js/dist/driver.css'
import { type DriveStep, driver } from 'driver.js'
import { createApp, h } from 'vue'

import TutorialCard from '@/components/shared/TutorialCard.vue'

import type { IStep, ITutorial } from '@/interfaces/tutorial'

function formatSteps(steps: IStep[]): DriveStep[] {
  return steps.map((step) => {
    const targetSelector = step.targetId.startsWith('#') ? step.targetId : `#${step.targetId}`

    return {
      element: targetSelector,
      popover: {
        align: step.align,
        description: step.description,
        side: step.side,
        title: step.title,
      },
    } as DriveStep
  })
}

export const useTutorial = (config: ITutorial) => {
  const mountElement = document.createElement('div')
  let tutorialApp: ReturnType<typeof createApp> | null = null

  const driverInstance = driver({
    onDestroyed: () => {
      if (tutorialApp) {
        tutorialApp.unmount()
        tutorialApp = null
      }
      mountElement.remove()
    },
    onPopoverRender: (popover, { driver }) => {
      if (!popover.wrapper.contains(mountElement)) {
        popover.wrapper.appendChild(mountElement)
      }

      const stepIndex = driver.getActiveIndex() ?? 0
      const currentStep = config.steps[stepIndex]

      if (tutorialApp) {
        tutorialApp.unmount()
        tutorialApp = null
      }

      tutorialApp = createApp({
        render() {
          return h(TutorialCard, {
            description: currentStep.description,
            link: currentStep.link,
            imagePath: currentStep.imagePath,
            isFirstStep: driver.isFirstStep(),
            isLastStep: driver.isLastStep(),
            onFinish: (skip?: boolean) => {
              driverInstance.destroy()
              if (config.onFinish) config.onFinish(skip)
            },
            onNextStep: () => {
              driverInstance.moveNext()
              driverInstance.refresh()
            },
            onPreviousStep: () => driverInstance.movePrevious(),
            stepIndex: stepIndex + 1,
            steps: config.steps,
            title: currentStep.title,
          })
        },
      })

      tutorialApp.mount(mountElement)
    },
    showButtons: [],
    showProgress: false,
    steps: formatSteps(config.steps),
  })

  driverInstance.drive()
}
