import { analysisSteps } from "@/config/analysis-steps";
import StepItem from "./components/StepItem";

interface StepperProps {
  currentStep: number;
}

export default function Stepper({
  currentStep,
}: StepperProps) {
  return (
    <div className="rounded-xl border bg-white p-6">

      <div className="flex">

        {analysisSteps.map((step) => (
          <StepItem
            key={step.id}
            step={step.id}
            title={step.title}
            active={step.id === currentStep}
          />
        ))}

      </div>

    </div>
  );
}