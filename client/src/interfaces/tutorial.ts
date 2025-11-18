import type { Alignment, Side } from 'driver.js'

export interface IStep {
  targetId: string
  imagePath?: string
  title?: string
  description: string | Array<string>
  align?: Alignment
  side?: Side
  link?: {
    url: string
    label: string
  }
}

export interface ITutorial {
  steps: Array<IStep>
  onFinish?: (skip?: boolean) => void
}

export interface ITutorialCard {
  description: string | Array<string>
  title?: string
  stepIndex: number
  isFirstStep: boolean
  isLastStep: boolean
  imagePath?: string
  link?: {
    url: string
    label: string
  }
  steps: Array<IStep>
  onNextStep: () => void
  onPreviousStep: () => void
  onFinish: (skip?: boolean) => void
}
