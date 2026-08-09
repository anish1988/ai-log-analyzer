export interface AnalysisStep {
  id: number;
  title: string;
}

export const analysisSteps: AnalysisStep[] = [
  {
    id: 1,
    title: "Search Logs",
  },
  {
    id: 2,
    title: "Error Preview",
  },
  {
    id: 3,
    title: "AI Analysis",
  },
  {
    id: 4,
    title: "Summary",
  },
];