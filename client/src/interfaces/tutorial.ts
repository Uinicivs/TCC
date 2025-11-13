import type { Alignment, Side } from 'driver.js'

export interface IStep {
  targetId: string
  imagePath?: string
  title?: string
  description: string
  align?: Alignment
  side?: Side
}

export interface ITutorial {
  steps: Array<IStep>
  onFinish?: (skip?: boolean) => void
}

export interface ITutorialCard {
  description: string
  title?: string
  stepIndex: number
  isFirstStep: boolean
  isLastStep: boolean
  imagePath?: string
  steps: Array<IStep>
  onNextStep: () => void
  onPreviousStep: () => void
  onFinish: (skip?: boolean) => void
}
